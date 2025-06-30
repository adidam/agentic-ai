from kiteconnect import KiteConnect
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Step 1: Correct API key
api_key = os.getenv("KITE_API_KEY")
api_secret = os.getenv("KITE_API_SECRET")

kite = KiteConnect(api_key=api_key)

# Step 2: Use login flow to get request_token (via browser)
print(kite.login_url())

# After login redirect, you'll get: ?request_token=XYZ&action=login
access_token = os.getenv("KITE_ACCESS_TOKEN")
if (access_token == None):
    request_token = input("enter request token from url: ")

    # Step 3: Generate session
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    with open(".env", "a") as f:
        f.write(f"\nKITE_ACCESS_TOKEN={access_token}")

print(access_token)

# Step 4: Set token for future use
kite.set_access_token(access_token)

# Step 5: Test market data
exchange = "NSE"
symbol = "INFY"
quote = kite.ohlc(f"{exchange}:{symbol}")
print(quote)

instruments = kite.instruments(exchange)

match = [inst for inst in instruments if inst['tradingsymbol'] == symbol]
print(match)

quote = kite.quote(["NSE:INFY"])
print(f"quote: {quote}")

# if match != None:
#     to_date = datetime.now()
#     from_date = to_date - timedelta(days=1)
#     data = kite.historical_data(
#         match[0]["instrument_token"], from_date, to_date, "5minute")
#     print(data)
