import datetime
import logging
import os
import sys
import pandas
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Tuple, Iterable, Dict, Any

import bitmex

import agg
from agg import riskratios


def assert_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if not env_value:
        raise EnvironmentError('missing environment variable: "{}"'.format(env_name))

    return env_value


def main():
    pandas.options.display.width = 0
    api_access_key = assert_env('BITMEX_API_ACCESS_KEY')
    api_secret_key = assert_env('BITMEX_API_SECRET_KEY')
    bitmex_client = agg.bitmex_client(api_access_key, api_secret_key)

    df_bitmex = pandas.DataFrame(list(agg.bitmex_load_positions(bitmex_client)))
    print(df_bitmex)
    df_bitmex.to_excel('../resources/bitmex_pos.xlsx')

    ratios = riskratios.report(bitmex_client)
    print(ratios)
    return
    print ('...........')

    api_access_key = assert_env('DERIBIT_API_ACCESS_KEY')
    api_secret_key = assert_env('DERIBIT_API_SECRET_KEY')
    deribit_private, deribit_public = agg.deribit_client(api_access_key, api_secret_key)

    positions = list(agg.deribit_load_positions(deribit_private))

    df_deribit_fut = pandas.DataFrame((position for position in positions if position['kind'] == 'future'))
    df_deribit_fut.to_excel('../resources/deribit_fut_pos.xlsx')
    print(df_deribit_fut)

    df_deribit_opt = pandas.DataFrame((position for position in positions if position['kind'] == 'option'))
    df_deribit_opt.to_excel('../resources/deribit_opt_pos.xlsx')
    print(df_deribit_opt)

    return


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