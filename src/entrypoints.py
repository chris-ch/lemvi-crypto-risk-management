import json
import os
from datetime import date, datetime
from typing import Any

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
    raise TypeError ("Type %s not serializable" % type(obj))


def load_bitmex_transactions(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    start_date = parse_date(assert_input('start_date', request_json))
    end_date = parse_date(assert_input('end_date', request_json))
    symbol = assert_input('symbol', request_json, 'XBT')
    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    client = agg.bitmex_client(api_access_key, api_secret_key)
    results = list(agg.bitmex_load_transactions(client, symbol, start_date, end_date))
    return json.dumps(results, default=json_serial)

if __name__ == '__main__':
    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    client = agg.bitmex_client(api_access_key, api_secret_key)
    print(list(agg.bitmex_load_transactions(client, 'XBT', date(2021, 1, 1), date(2021, 1, 5))))