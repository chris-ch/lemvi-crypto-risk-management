import json
import os
from datetime import date, datetime
from typing import Any

import flask

import agg


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


def assert_input(env_name: str, request_json: Any, input_default: Any=None) -> str:
    if env_name not in request_json and input_default is None:
        raise AttributeError('missing input field: "{}"'.format(env_name))

    if env_name not in request_json and input_default is not None:
        return input_default

    return request_json[env_name]


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
    raise TypeError("Type %s not serializable" % type(obj))


def load_bitmex_wallet_data(request: flask.Request):
    """Responds to any HTTP request.
    Example message {"since_date": "2021-01-04"}
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    since_date = None
    if 'since_date' in request_json:
        since_date = parse_date(request_json[since_date])

    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    client = agg.bitmex_client(api_access_key, api_secret_key)
    results = list(agg.bitmex_load_wallet_history(client, since_date))
    return json.dumps(results, default=json_serial)


def load_bitmex_orders_data(request: flask.Request):
    """Responds to any HTTP request.
    Example message {"since_date": "2021-01-04"}
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    since_date = None
    if 'since_date' in request_json:
        since_date = parse_date(request_json[since_date])

    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    client = agg.bitmex_client(api_access_key, api_secret_key)
    results = list(agg.bitmex_load_orders(client, since_date))
    return json.dumps(results, default=json_serial)
