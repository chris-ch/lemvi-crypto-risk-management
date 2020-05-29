import datetime
import logging
import os
import sys
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Tuple, Iterable, Dict, Any

import deribit
from deribit import PublicApi, PrivateApi


def authenticate(api_access_key: str, api_secret_key: str) -> Tuple[PrivateApi, PublicApi]:
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


def load_trades(private_api: PrivateApi, currency: DeribitCurrency, start_date: date, end_date : date) -> Iterable[Dict[str, Any]]:
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


def exec_requests(private_api: PrivateApi, public_api: PublicApi):

    response = private_api.private_get_subaccounts_get()
    print(response['result'])

    today = date.today()
    first_day_current_month = today.replace(day=1)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    trades = load_trades(private_api, DeribitCurrency.BTC, first_day_prev_month, last_day_prev_month)
    print(len(trades), trades)
    for trade in trades:
        print(trade)


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


def main():
    api_access_key = assert_env('DERIBIT_API_ACCESS_KEY')
    api_secret_key = assert_env('DERIBIT_API_SECRET_KEY')
    private_api, public_api = authenticate(api_access_key, api_secret_key)
    exec_requests(private_api, public_api)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    log_name = os.path.abspath(sys.argv[0]).split(os.sep)[-1].split('.')[0]
    file_handler = logging.FileHandler(log_name + '.log', mode='w')
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)
    try:
        main()

    except SystemExit:
        pass

    except:
        logging.exception('error occurred', sys.exc_info()[0])
        raise
