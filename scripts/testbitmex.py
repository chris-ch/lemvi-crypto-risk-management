import logging
import os
import sys
from datetime import date

import pandas

import agg


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


def main():
    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    client = agg.bitmex_client(api_access_key, api_secret_key)
    start_date = date(2020, 6, 9)
    end_date = date(2020, 10, 1)
    results = list(agg.bitmex_load_transactions(client, 'XBT', start_date, end_date))
    df = pandas.DataFrame(results)
    df.to_json('trades-xbt.json', orient='records', date_format='iso')


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
