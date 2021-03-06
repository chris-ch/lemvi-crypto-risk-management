import unittest
from datetime import date

import agg
import entrypoints


class TestEntryPoints(unittest.TestCase):

    def test_basic(self):
        api_access_key = entrypoints.assert_env('BITMEX_API_ACCESS_KEY')
        api_secret_key = entrypoints.assert_env('BITMEX_API_SECRET_KEY')
        client = agg.bitmex_client(api_access_key, api_secret_key)
        for count, item in enumerate(agg.bitmex_load_wallet_history(client, date(2021, 1, 1))):
            print(count, item)


if __name__ == '__main__':
    unittest.main()
