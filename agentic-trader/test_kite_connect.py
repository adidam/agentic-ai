from kite_connect import fetch_historical, fetch_top_volume, is_valid_symbol, fetch_quote
from unittest import TestCase


class KiteConnectTest(TestCase):
    def get_symbol(exg_symbol):
        symbol = is_valid_symbol('INFY')
        return symbol

    def test_symbol_valid(self):
        self.assertIsNotNone(self.get_symbol())

    def test_fetch_historical(self):
        symbol = self.get_symbol()
        print(f"symbol: {symbol}")
        history = fetch_historical(symbol['tradingsymbol'])
        if history:
            print(f"history of {symbol}, {len(history)}")
        else:
            print(f"No history found for {symbol}")

    def test_fetch_top_volume(self):
        symbols = fetch_top_volume()
        self.assertIsNot(len(symbols), 0)
