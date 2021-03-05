import logging
import os
import sys

import agg


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


def main():
    api_access_key = assert_env('DERIBIT_API_ACCESS_KEY')
    api_secret_key = assert_env('DERIBIT_API_SECRET_KEY')
    private_api, public_api = agg.deribit_client(api_access_key, api_secret_key)
    #exec_requests(private_api, public_api)
    print(list(agg.deribit_load_positions(private_api)))


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
