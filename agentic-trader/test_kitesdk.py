from unittest import TestCase
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


class KiteSdkTestCase(TestCase):

    def setUp(self):
        load_dotenv()

        # Step 1: Correct API key
        api_key = os.getenv("KITE_API_KEY")
        api_secret = os.getenv("KITE_API_SECRET")

        self.kite = KiteConnect(api_key=api_key)

        # Step 2: Use login flow to get request_token (via browser)
        print(self.kite.login_url())

        self.exchange = 'NSE'
        # After login redirect, you'll get: ?request_token=XYZ&action=login
        access_token = os.getenv("KITE_ACCESS_TOKEN")

        if (access_token == None):
            request_token = input("enter request token from url: ")
            # Step 3: Generate session
            data = self.kite.generate_session(
                request_token, api_secret=api_secret)
            access_token = data["access_token"]

        print(access_token)

        # Step 4: Set token for future use
        self.kite.set_access_token(access_token)

    def test_profile(self):
        profile = self.kite.profile()
        self.assertIsNotNone(profile)

    def test_ohlc(self):
        # Step 5: Test market data
        symbol = "INFY"
        quote = self.kite.ohlc(f"{self.exchange}:{symbol}")

        self.assertIsNotNone(quote)

    def test_instruments(self):
        symbol = 'INFY'
        instruments = self.kite.instruments(self.exchange)

        match = [inst for inst in instruments if inst['tradingsymbol'] == symbol]

        self.assertIsNotNone(match, f"Match found for {symbol}")

        quote = self.kite.quote(["NSE:INFY"])
        print(f"quote: {quote}")

        self.assertIsNotNone(quote)
