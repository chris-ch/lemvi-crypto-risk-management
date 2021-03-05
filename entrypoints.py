import json
import os
from datetime import date

import agg


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


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
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
        api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
        client = agg.bitmex_client(api_access_key, api_secret_key)
        start_date = date(2020, 6, 9)
        end_date = date(2020, 10, 1)
        results = list(agg.bitmex_load_transactions(client, 'XBT', start_date, end_date))
        return json.dumps(results)
