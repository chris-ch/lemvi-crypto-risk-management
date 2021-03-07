from logging.config import dictConfig
from flask import Flask
from flask import request

import entrypoints


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)


@app.route('/orders-data', methods=['POST'])
def orders_data():
    return entrypoints.load_bitmex_orders_data(request)


@app.route('/wallet-data', methods=['POST'])
def wallet_data():
    return entrypoints.load_bitmex_wallet_data(request)
