import json
import os
from google.cloud import pubsub_v1
from datetime import date, datetime
from typing import Any

import flask
from flask import current_app
from flask.json import JSONEncoder

import agg


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


def assert_input(input_name: str, request_json: Any, input_default: Any=None) -> str:
    if input_name not in request_json and input_default is None:
        raise AttributeError('missing input field: "{}"'.format(input_name))

    if input_name not in request_json and input_default is not None:
        return input_default

    return request_json[input_name]


def parse_date(yyyymmdd: str) -> date:
    if len(yyyymmdd) == 8:
        year = yyyymmdd[:4]
        month = yyyymmdd[4:6]
        day = yyyymmdd[6:8]
    else:
        year, month, day = yyyymmdd.split('-')[:3]

    return date(int(year), int(month), int(day))


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError('Type %s not serializable' % type(obj))


def load_bitmex_wallet_data(request: flask.Request):
    """Responds to any HTTP request.
    Example message {"since_date": "2021-01-04"}
    Returns:
        The response text or any set of values that can be turned into a Response object using
        `make_response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    since_date = None
    if 'since-date' in request_json:
        since_date = parse_date(request_json['since-date'])

    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    google_cloud_project = assert_env('GOOGLE_CLOUD_PROJECT')
    client = agg.bitmex_client(api_access_key, api_secret_key)
    results = agg.bitmex_load_wallet_history(client, since_date)
    count = 0
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(google_cloud_project, 'job-wallet-data-import')

    for result in results:
        print(result)
        count += 1
        filename = create_transaction_filename(result['transactID'], 'bitmex', result['transactTime'], result['account'], result['currency'], result['address'], result['transactType'], result['transactStatus'])
        future = publisher.publish(topic_path, json.dumps({'filename': filename, 'data': result}, default=json_serial), origin='load_bitmex_wallet_data')
        future.result()

    return flask.jsonify(count=count)


def load_bitmex_orders_data(request: flask.Request):
    """Responds to any HTTP request.
    Example message {"since_date": "2021-01-04"}
    Returns:
        The response text or any set of values that can be turned into a Response object using
        `make_response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    since_date = None
    if 'since-date' in request_json:
        since_date = parse_date(request_json['since-date'])

    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    google_cloud_project = assert_env('GOOGLE_CLOUD_PROJECT')

    client = agg.bitmex_client(api_access_key, api_secret_key)
    results = agg.bitmex_load_orders(client, since_date)
    count = 0
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(google_cloud_project, 'job-order-data-import')

    for result in results:
        count += 1
        filename = create_order_filename(result['orderID'], 'bitmex', result['transactTime'], result['account'], result['symbol'], result['side'], result['currency'], result['settlCurrency'], result['ordStatus'])
        future = publisher.publish(topic_path, json.dumps({'filename': filename, 'data': result}, default=json_serial), origin='load_bitmex_orders_data')
        future.result()

    return flask.jsonify(count=count)


def create_order_filename(order_id: str, exchange: str, transact_time: datetime, account: str, symbol: str, buy_sell: str, currency: str, settlement_currency: str, order_status: str):
    filename = '{}_{}_{}_{}_{}_{}_{}.json'.format(order_id, account, symbol, buy_sell, currency, settlement_currency, order_status)
    return '/'.join(['orders', exchange, str(transact_time.year), str(transact_time.month).zfill(2), str(transact_time.day).zfill(2), filename])


def create_transaction_filename(transaction_id: str, exchange: str, transact_time: datetime, account: str, currency: str, address: str, transaction_type: str, transaction_status: str):
    filename = '{}_{}_{}_{}_{}_{}.json'.format(transaction_id, account, currency, address, transaction_type, transaction_status)
    return '/'.join(['wallet', exchange, str(transact_time.year), str(transact_time.month).zfill(2), str(transact_time.day).zfill(2), filename])


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date) or isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def jsonify(items):
    current_app.json_encoder = CustomJSONEncoder
    return flask.jsonify(items)