import logging
from datetime import datetime, date, timedelta
import json
from enum import Enum
from functools import lru_cache
from typing import Dict, Any, Iterable, Tuple, Generator

import bitmex
import pandas
from bravado.client import SwaggerClient

import deribit
from deribit import PublicApi, PrivateApi


def bitmex_client(api_access_key: str, api_secret_key: str) -> bitmex:
    return bitmex.bitmex(test=False, api_key=api_access_key, api_secret=api_secret_key)


def bitmex_user_account(client: SwaggerClient) -> Dict[str, Any]:
    result, status = client.User.User_getMargin(currency='XBt').result()
    if status.status_code not in (200, 201, 204):
        raise ConnectionError('failed to retrieve margin data: %s %s %s' % (status.status_code, status.text, status.reason))

    return result


def bitmex_load_positions(client: SwaggerClient) -> Generator[Dict[str, Any], None, None]:
    count = 0
    columns = ['account', 'symbol', 'currency', 'underlying', 'quoteCurrency', 'currentQty',
               'markPrice', 'markValue', 'homeNotional', 'foreignNotional', 'initMarginReq', 'maintMarginReq',
               'initMargin', 'maintMargin', 'openingQty', 'openingCost',
               'liquidationPrice', 'bankruptPrice', 'leverage', 'unrealisedPnl']
    results, status = client.Position.Position_get(columns=json.dumps(columns)).result()
    if status.status_code not in (200, 201):
        raise ConnectionError('failed to load trades: %s %s %s' % (status.status_code, status.text, status.reason))

    for result in results:
        count += 1
        yield {k: v for k, v in result.items() if k in columns}


def bitmex_load_instrument(client: SwaggerClient, symbol: str) -> Dict[str, Any]:
    results, status = client.Instrument.Instrument_get(symbol=symbol, count=1).result()
    if status.status_code not in (200, 201):
        raise ConnectionError('failed to load trades: %s %s %s' % (status.status_code, status.text, status.reason))

    if len(results) > 0:
        return results[0]

    else:
        return dict()


def bitmex_load_trades(client: SwaggerClient, start_date: datetime, end_date: datetime):
    results_count = 100
    count = 0
    results, status = client.Execution.Execution_getTradeHistory(count=results_count, startTime=start_date, endTime=end_date, start=0).result()
    if status.status_code not in (200, 201):
        raise ConnectionError('failed to load trades: %s %s %s' % (status.status_code, status.text, status.reason))

    for result in results:
        count += 1
        yield result

    while len(results) == results_count:
        results, status = client.Execution.Execution_getTradeHistory(count=results_count, startTime=start_date, endTime=end_date, start=count).result()
        if status.status_code not in (200, 201):
            raise ConnectionError('failed to load trades: %s %s %s' % (status.status_code, status.text, status.reason))

        for result in results:
            count += 1
            yield result


def deribit_client(api_access_key: str, api_secret_key: str) -> Tuple[PrivateApi, PublicApi]:
    # Setup configuration instance
    conf = deribit.configuration.Configuration()
    # Setup unauthenticated client
    client = deribit.api_client.ApiClient(conf)
    public_api = PublicApi(client)
    # Authenticate with API credentials
    response = public_api.public_auth_get('client_credentials', '', '', api_access_key, api_secret_key, '', '', '', scope='session:test wallet:read')
    access_token = response['result']['access_token']

    conf_authed = deribit.configuration.Configuration()
    conf_authed.access_token = access_token
    # Use retrieved authentication token to setup private endpoint client
    client_authed = deribit.api_client.ApiClient(conf_authed)
    private_api = PrivateApi(client_authed)
    return private_api, public_api


class DeribitCurrency(Enum):
    BTC = 'BTC'
    ETH = 'ETH'


def deribit_load_trades(private_api: PrivateApi, currency: DeribitCurrency, start_date: date, end_date : date) -> Iterable[Dict[str, Any]]:
    start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp()) * 1000
    end_timestamp = int(datetime.combine(end_date, datetime.max.time()).timestamp()) * 1000 + 999
    count = 50
    include_old = 'true'

    logging.info('requesting trades start date: {}'.format(datetime.combine(start_date, datetime.min.time())))
    logging.info('requesting trades end date: {}'.format(datetime.combine(end_date, datetime.max.time())))
    logging.info('requesting trades from {} through {}'.format(start_timestamp, end_timestamp))
    trades = list()
    has_more = True
    retrieve_trades_func = private_api.private_get_user_trades_by_currency_and_time_get
    while has_more:
        api_response = retrieve_trades_func(currency.name, start_timestamp, end_timestamp, count=count, include_old=include_old, sorting='asc')
        trades += api_response['result']['trades']
        has_more = api_response['result']['has_more']
        if has_more:
            start_timestamp = trades[-1]['timestamp'] + 1

    return trades


def deribit_exec_requests(private_api: PrivateApi, public_api: PublicApi):

    response = private_api.private_get_subaccounts_get()
    print(response['result'])

    today = date.today()
    first_day_current_month = today.replace(day=1)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    trades = deribit_load_trades(private_api, DeribitCurrency.BTC, first_day_prev_month, last_day_prev_month)
    print(trades)
    df = pandas.DataFrame(trades)
    print(df.to_json())


def deribit_load_positions(private_api):
    retrieve_positions_func = private_api.private_get_positions_get

    btc_positions = retrieve_positions_func(currency='BTC')['result']
    for position in btc_positions:
        yield position

    eth_positions = retrieve_positions_func(currency='ETH')['result']
    for position in eth_positions:
        yield position
