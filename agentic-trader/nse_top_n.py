from io import BytesIO
import requests
import pandas as pd

# NSE URL for gainers (can change this later to volume API)
base_url = "https://www.niftyindices.com/IndexConstituent/"

# Build the filename for the CSV file


def build_filename(index_name: str = 'nifty', top_n: int = 50) -> str:
    return f"ind_nifty{index_name}{top_n}list.csv"


def fetch_nifty_top_n_list(index_name: str, top_n: int) -> list[str]:
    csv_name = build_filename(index_name, top_n)
    url = base_url + csv_name
    # Proper browser-like headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://niftyindices.com/",
        "Connection": "keep-alive",
        "Host": "www.niftyindices.com",
    }

    # Create session and set cookies from initial request
    with requests.Session() as session:
        # This sets the required cookies
        session.get("https://www.niftyindices.com", headers=headers)

        # Now fetch data using the same session
        response = session.get(url, headers=headers)

        # Check if we got a valid response
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return []
        else:
            df = pd.read_csv(BytesIO(response.content))
            symbols = df['Symbol'].tolist()
            return symbols
