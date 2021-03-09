import unittest
from datetime import date

import agg
import entrypoints
from util import parse_iso8601


class TestEntryPoints(unittest.TestCase):

    def test_basic(self):
        api_access_key = entrypoints.assert_env('BITMEX_API_ACCESS_KEY')
        api_secret_key = entrypoints.assert_env('BITMEX_API_SECRET_KEY')
        client = agg.bitmex_client(api_access_key, api_secret_key)
        for count, item in enumerate(agg.bitmex_load_wallet_history(client, date(2021, 1, 1))):
            print(count, item)

    def test_parse_iso_date(self):
        date_str = '2021-02-05T20:21:28.674000+00:00'
        self.assertEqual(2021, parse_iso8601(date_str).date().year)

if __name__ == '__main__':
    unittest.main()
