import datetime
import json
import logging
import os
import sys
import pandas
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Tuple, Iterable, Dict, Any

import bitmex
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsResponseAdapter


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


def bitmex_load_positions(client):
    count = 0
    columns = ['account', 'symbol', 'currency', 'underlying', 'quoteCurrency', 'currentQty',
               'markPrice', 'markValue', 'homeNotional', 'foreignNotional']
    results, status = client.Position.Position_get(columns=json.dumps(columns)).result()
    if status.status_code not in (200, 201):
        raise ConnectionError('failed to load trades: %s %s %s' % (status.status_code, status.text, status.reason))

    for result in results:
        count += 1
        yield {k: v for k, v in result.items() if k in columns}


def bitmex_load_trades(client, start_date, end_date):
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


def main():
    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    client = bitmex.bitmex(test=False, api_key=api_access_key, api_secret=api_secret_key)
    #results, status = client.Trade.Trade_get().result()
    #results, status = bitmex_load(client.Position.Position_get)
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2020, 2, 1)
    for result in bitmex_load_positions(client):
        print(result)

    #df = pandas.DataFrame(results)
    #print(df.to_json())
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    log_name = os.path.abspath(sys.argv[0]).split(os.sep)[-1].split('.')[0]
    file_handler = logging.FileHandler('../logs/' + log_name + '.log', mode='w')
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
