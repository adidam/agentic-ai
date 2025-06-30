from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

load_dotenv()

kite_api_key = os.getenv("KITE_API_KEY")

kite = KiteConnect(api_key=kite_api_key)
print(kite.login_url())  # Open this in browser

api_secret = os.getenv("KITE_API_SECRET")
access_token = os.getenv("KITE_ACCESS_TOKEN")
access_token = 'e6BrxylF42AVgajAlp6umz0V9iWXfMpG'
print(f"access token: {access_token}")

if access_token == None:
    request_token_from_url = input("Enter the request token from the URL: ")
    data = kite.generate_session(request_token_from_url, api_secret=api_secret)
    access_token = data["access_token"]

    with open(".env", 'a') as f:
        f.write(f"\nKITE_ACCESS_TOKEN={access_token}")

kite.set_access_token(access_token)

print(kite.profile())
print(f"Successfully connected to kite. {access_token}")
