from datetime import datetime
import json
import pandas as pd
from kite_connect import kite
from kite_connect import fetch_quote
import os


def get_top_nse_stocks_by_volume(n=10):
    instruments = kite.instruments("NSE")
    [inst.update({'tradedVolume': 0.0}) for inst in instruments]
    df = pd.DataFrame(instruments)
    print(df.columns)
    for index, row in df.iterrows():
        data = fetch_quote(symbol=row['tradingsymbol'])
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


def validate_json_string(json_string):
    """
    Validates if a string is valid JSON.
    Returns (is_valid, error_message)
    """
    try:
        json.loads(json_string)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def validate_json_file(file_path):
    """
    Validates if a file contains valid JSON.
    Returns (is_valid, error_message)
    """
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True, None
    except FileNotFoundError:
        return False, f"File not found: {file_path}"
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def safe_json_load(file_path, default=None):
    """
    Safely loads JSON from file with error handling.
    Returns the parsed JSON or default value if loading fails.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load JSON from {file_path}: {e}")
        return default


def safe_json_dump(data, file_path, **kwargs):
    """
    Safely dumps data to JSON file with error handling.
    Returns True if successful, False otherwise.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(data, f, **kwargs)
        return True
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")
        return False


def validate_json_structure(data, required_keys=None, optional_keys=None):
    """
    Validates JSON structure against expected keys.
    Returns (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"

    if required_keys:
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            return False, f"Missing required keys: {missing_keys}"

    if optional_keys:
        unexpected_keys = [
            key for key in data if key not in required_keys + optional_keys]
        if unexpected_keys:
            return False, f"Unexpected keys: {unexpected_keys}"

    return True, None
