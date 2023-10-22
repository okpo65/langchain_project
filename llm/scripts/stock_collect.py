from datetime import date, timedelta, datetime

import requests

from config.settings import POLYGON_API_KEY
from llm.models import Stock


def get_stocks(symbols, start_date, end_date):

    for symbol in symbols:
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
        res = requests.get(url).json()

        for stock in res['results']:
            Stock.objects.get_or_create(symbol=res['ticker'],
                                        highest_price=stock['h'],
                                        lowest_price=stock['l'],
                                        close_price=stock['c'],
                                        date=datetime.fromtimestamp(int(stock['t'])/1000))


def run():
    start_date = date.today() - timedelta(days=7)
    end_date = date.today()

    get_stocks(['TSLA', 'AAPL', 'META', 'AMZN', 'NFLX'], start_date, end_date)
