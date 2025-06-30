from nsepython import *


def get_price_volume(object):
    ltp = 0.0
    ttv = 0.0
    if object:
        if 'priceInfo' in object and 'lastPrice' in object['priceInfo']:
            ltp = object['priceInfo']['lastPrice']
        if 'preOpenMarket' in object and 'totalTradedVolume' in object['preOpenMarket']:
            ttv = object['preOpenMarket']['totalTradedVolume']

    return (ltp, ttv)


def fetch_price_volume(symbol: str):
    # Fetch all equity data
    data = None
    try:
        data = nse_eq(symbol)
    except requests.exceptions.ReadTimeout:
        print(f'Skipping {symbol}...')
    except Exception as e:
        print(f'error fetching {symbol}: {str(e)}')
    time.sleep(1.5)
    return get_price_volume(data)
