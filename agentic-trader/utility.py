from datetime import datetime
import json
import pandas as pd
from kite_connect import kite
from nse_connect import fetch_price_volume


def get_top_nse_stocks_by_volume(n=10):
    instruments = kite.instruments("NSE")
    [inst.update({'tradedVolume': 0.0}) for inst in instruments]
    df = pd.DataFrame(instruments)
    print(df.columns)
    for index, row in df.iterrows():
        data = fetch_price_volume(row['tradingsymbol'])
        row['last_price'] = data[0]
        row['tradedVolume'] = data[1]

    df = df[df["instrument_type"] == "EQ"]
    df = df[df["segment"] == "NSE"]
    df = df[df["last_price"] > 100]  # avoid penny stocks
    # discard ones more that the total budget
    df = df[df["last_price"] < 10000]
    top = df.sort_values(by="last_price", ascending=False).head(n)
    return ["NSE:" + s for s in top["tradingSymbol"].tolist()]


def fetch_and_save_top_nse_symbols(n=10, outfile="top_symbols.json"):
    top_symbols = get_top_nse_stocks_by_volume(n)
    print(top_symbols)
    # Save to file
    if (len(top_symbols) > 0):
        result = {
            "timestamp": datetime.now().isoformat(),
            "symbols": top_symbols
        }

        with open(outfile, "w") as f:
            json.dump(result, f, indent=2)

        print(f"✅ Top {n} NSE symbols {top_symbols} saved to {outfile}")
    return top_symbols


def load_top_symbols(file_path="top_symbols.json"):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        top_symbols = fetch_and_save_top_nse_symbols(10)
        if len(top_symbols) == 0:
            print(f"ERROR: No symbols found. {top_symbols}")
        return top_symbols

    return data["symbols"]
