from io import BytesIO
import requests
import pandas as pd

# NSE URL for gainers (can change this later to volume API)
base_url = "https://www.niftyindices.com/IndexConstituent/"
base_path = "./out/data/"


def build_filename(index_name: str = 'nifty', top_n: int = 50) -> str:
    # Build the filename for the CSV file
    return f"ind_nifty{index_name}{top_n}list.csv"


def fetch_nifty_top_n_list(index_name: str, top_n: int = 50) -> list[str]:
    csv_name = build_filename(index_name, top_n)
    try:
        with open(base_path + csv_name, "r") as f:
            print(f"Fetching file locally: {csv_name}")
            df = pd.read_csv(f)
            symbols = df['Symbol'].tolist()
            return symbols
    except:
        print(f"{csv_name} not available fetching from the web.")
        if fetch_nifty_top_n_list_web(csv_name, top_n):
            return fetch_nifty_top_n_list(index_name, top_n)
        return []


def fetch_nifty_top_n_list_web(index_name: str, top_n: int) -> list[str]:
    url = base_url + index_name
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
            return False
        else:
            with open(base_path + index_name, "w") as f:
                f.write(BytesIO(response.content))
                f.close()
            return True
