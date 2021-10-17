import json
import os

from threading import Thread

from flask import Flask, make_response, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

db_name = 'tickers.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Ticker(db.Model):
    __tablename__ = 'tickers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    last_trade = db.Column(db.Float, nullable=False)


@app.route("/")
def send_tickers():
    if request.method != 'GET':
        return make_response('Malformed request', 400)
    headers = {"Content-Type": "application/json"}
    tickers = Ticker.query.all()
    response_dict = {}
    for ticker in tickers:
        ticker_dict = {ticker.symbol: {'price': ticker.price, 'volume': ticker.volume, 'last_trade': ticker.last_trade}}
        response_dict.update(ticker_dict)
    response_data = json.dumps(response_dict)
    return make_response(response_data, 200, headers)


if __name__ == "__main__":
    updater = Thread(target=os.system, args=('db_manager.py',), daemon=True)
    updater.start()
    test = Thread(target=os.system, args=('test.py',), daemon=True)
    test.start()
    app.run(debug=False)
