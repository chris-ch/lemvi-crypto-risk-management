import datetime
import logging
import os
import sys
from datetime import datetime
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
    #results, status = client.Trade.Trade_get().result()
    #results, status = bitmex_load(client.Position.Position_get)
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2020, 2, 1)
    for result in agg.bitmex_load_positions(client):
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
