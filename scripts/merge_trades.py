import datetime
import logging
import os
import sys
import pandas
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Tuple, Iterable, Dict, Any

import bitmex


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


def main():
    df_bitmex = pandas.read_json('../resources/bitmex-trades.json')
    df_deribit = pandas.read_json('../resources/deribit-trades.json')
    pandas.options.display.width = 0
    print(df_bitmex)
    print(df_deribit)


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
