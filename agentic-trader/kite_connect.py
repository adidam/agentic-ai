from kite_session import kite
from nse_top_n import fetch_nifty_top_n_list


def list_symbols(exchange='NSE'):
    instruments = kite.instruments(exchange=exchange)
    return [inst['tradingsymbol'] for inst in instruments]


def is_valid_symbol(symbol: str, segment="NSE"):
    instruments = kite.instruments(segment)
    symbol_filter = [
        inst for inst in instruments if inst['tradingsymbol'] == symbol]
    return symbol_filter[0] if len(symbol_filter) > 0 else None


def fetch_quote(symbol: str, exchange="NSE"):
    data = kite.quote([f"{exchange}:{symbol}"])
    return data[f'{exchange}:{symbol}']


def fetch_historical(symbol, segment="NSE", interval="5minute", duration="day"):
    from datetime import datetime, timedelta
    instrument = is_valid_symbol(symbol, segment)
    if instrument == None:
        print("Instrument is null.")
        return None

    to_date = datetime.now()
    from_date = to_date - timedelta(days=1)
    data = kite.historical_data(
        instrument["instrument_token"], from_date, to_date, interval)
    print(f"Historical data length: {len(data)}")
    return data if data else None


def fetch_top_volume(exchange: str = "NSE", index_nifty: str = "", size: int = 50):
    nifty_50_list = fetch_nifty_top_n_list(index_name=index_nifty, top_n=size)
    # Fetch all instruments traded on NSE
    instruments = kite.instruments("NSE")
    # Filter only equity stocks
    stocks = [i for i in instruments if i['instrument_type'] == 'EQ']

    symbol_tokens = {f"{exchange}:{i['tradingsymbol']}": i['instrument_token']
                     for i in stocks if i['tradingsymbol'] in nifty_50_list}
    tokens = list(symbol_tokens.keys())

    # Split into batches of 50
    from itertools import islice

    def chunks(data, size=50):
        it = iter(data)
        for first in it:
            yield [first] + list(islice(it, size - 1))

    volume_data = []
    for batch in chunks(tokens):
        quotes = kite.quote(batch)
        for token in batch:
            q = quotes[token]
            volume_data.append({
                "token": q['instrument_token'],
                "symbol": token.split(":")[1],
                "volume": q['volume'],
                "last_price": q['last_price'],
                "ohlc": q['ohlc']
            })

    sorted_by_volume = sorted(
        volume_data, key=lambda x: x['volume'], reverse=True)
    top_traded = sorted_by_volume[:size]  # Top 50
    print(f"Top traded: {len(top_traded)}")
    return top_traded
