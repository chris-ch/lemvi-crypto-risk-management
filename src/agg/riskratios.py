from datetime import datetime, timedelta, timezone
from bravado.client import SwaggerClient

from agg import bitmex_user_account, bitmex_load_positions, bitmex_load_instrument


def bitmex_ratio_net_exposure(positions, account_data):
    wallet_balance = account_data['walletBalance']  # Deposits - Withdrawals + realised PNL
    unrealized_pnl = sum((position['unrealisedPnl'] for position in positions))
    margin_balance = wallet_balance / (wallet_balance + unrealized_pnl) - 1.
    return margin_balance


def bitmex_ratio_time_before_expiry(bitmex_instruments_data, as_of_date: datetime, notice_period_days: int):
    should_roll_instruments = list()
    for symbol in bitmex_instruments_data:
        instrument = bitmex_instruments_data[symbol]
        if instrument['expiry']:
            print(instrument['expiry'])
            print(instrument['expiry'] - timedelta(days=notice_period_days))
            print(as_of_date)
            within_notice_period = instrument['expiry'] - timedelta(days=notice_period_days) <= as_of_date
            if within_notice_period:
                should_roll_instruments.append({'symbol': symbol, 'expiry': instrument['expiry']})

    return ', '.join(['{symbol} ({expiry:%Y-%m-%d})'.format(**instr) for instr in should_roll_instruments])


def report(bitmex_client: SwaggerClient):
    bitmex_positions = list(bitmex_load_positions(bitmex_client))
    bitmex_account_data = bitmex_user_account(bitmex_client)
    bitmex_instruments_data = { pos['symbol']: bitmex_load_instrument(bitmex_client, pos['symbol']) for pos in bitmex_positions}
    now = datetime.now(tz=timezone.utc)
    ratios = dict()
    ratios['bitmex_ratio_max_net_exposure'] = bitmex_ratio_net_exposure(bitmex_positions, bitmex_account_data)
    ratios['bitmex_expiring_5d'] = bitmex_ratio_time_before_expiry(bitmex_instruments_data, now, 5)
    ratios['bitmex_expiring_10d'] = bitmex_ratio_time_before_expiry(bitmex_instruments_data, now, 10)
    ratios['bitmex_expiring_20d'] = bitmex_ratio_time_before_expiry(bitmex_instruments_data, now, 20)
    return ratios
