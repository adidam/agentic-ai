from kite_session import kite


def list_symbols(exchange='NSE'):
    instruments = kite.instruments(exchange=exchange)
    return [inst['tradingsymbol'] for inst in instruments]


def is_valid_symbol(symbol: str, segment="NSE"):
    instruments = kite.instruments(segment)
    return [inst for inst in instruments if inst['tradingsymbol'] == symbol][0]


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
