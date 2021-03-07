from datetime import date, datetime

from flask import Flask
from flask import request
from flask import jsonify
from flask.json import JSONEncoder

import entrypoints


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date) or isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder


@app.route('/orders-data', methods=['POST'])
def orders_data():
    return entrypoints.load_bitmex_orders_data(request)


@app.route('/wallet-data', methods=['POST'])
def wallet_data():
    return entrypoints.load_bitmex_wallet_data(request)
