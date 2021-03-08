import json
import os
from google.cloud import pubsub_v1
from datetime import date, datetime
from typing import Any, Iterable, Dict

import flask
from flask import current_app
from flask.json import JSONEncoder

import agg
from msgstore import FieldStoreFile, TopicId
from util import json_serial


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
    client = agg.bitmex_client(api_access_key, api_secret_key)
    results = agg.bitmex_load_wallet_history(client, since_date)
    count = store_results(results, 'bitmex', TopicId.JOB_WALLET_DATA_IMPORT.value, 'transactions', 'transactID', 'transactTime')
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

    client = agg.bitmex_client(api_access_key, api_secret_key)
    results = agg.bitmex_load_orders(client, since_date)
    count = store_results(results, 'bitmex', TopicId.JOB_ORDER_DATA_IMPORT.value, 'orders', 'orderID', 'transactTime')
    return flask.jsonify(count=count)


def store_results(results: Iterable[Dict], exchange: str, topic_id: str, kind: str, filename_part1: str, filename_part2: str):
    google_cloud_project = assert_env('GOOGLE_CLOUD_PROJECT')
    namespace_portfolio = assert_env('NAMESPACE_PORTFOLIO')
    count = 0
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(google_cloud_project, topic_id)
    for result in results:
        count += 1
        filename = create_filename(result[filename_part1], result[filename_part2])
        message = {
            FieldStoreFile.FILENAME.value: filename,
            FieldStoreFile.CONTENT.value: result,
            FieldStoreFile.NAMESPACE.value: namespace_portfolio,
            FieldStoreFile.SOURCE.value: kind,
            FieldStoreFile.EXCHANGE.value: exchange
        }
        future = publisher.publish(topic_path, json.dumps(message, default=json_serial).encode('utf-8'), origin='load_bitmex_data')
        future.result()
    return count


def create_filename(transaction_id: str, transact_time: datetime):
    filename = '{}_{}.json'.format(transact_time.date().isoformat(), transaction_id)
    return filename


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