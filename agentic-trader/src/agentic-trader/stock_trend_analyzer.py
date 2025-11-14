import yfinance as yf
import pandas as pd
import numpy as np

# --- Configuration ---
SMA_SHORT = 50
SMA_MEDIUM = 100
SMA_LONG = 200
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9


def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Calculates all necessary technical indicators (SMAs and MACD)."""
    if data.empty:
        return data

    # 1. Simple Moving Averages (SMAs)
    data[f'SMA_{SMA_SHORT}'] = data['Close'].rolling(window=SMA_SHORT).mean()
    data[f'SMA_{SMA_MEDIUM}'] = data['Close'].rolling(window=SMA_MEDIUM).mean()
    data[f'SMA_{SMA_LONG}'] = data['Close'].rolling(window=SMA_LONG).mean()

    # 2. Moving Average Convergence/Divergence (MACD)
    # Calculate 12-day EMA (Fast)
    data['EMA_Fast'] = data['Close'].ewm(span=MACD_FAST, adjust=False).mean()
    # Calculate 26-day EMA (Slow)
    data['EMA_Slow'] = data['Close'].ewm(span=MACD_SLOW, adjust=False).mean()
    # MACD Line
    data['MACD'] = data['EMA_Fast'] - data['EMA_Slow']
    # Signal Line (9-day EMA of MACD Line)
    data['MACD_Signal'] = data['MACD'].ewm(
        span=MACD_SIGNAL, adjust=False).mean()

    return data


def check_sma_stacking_signal(latest_data: pd.Series):
    """
    Checks for the confirmation of a strong, established trend (the original request).
    """
    # Helper function to get scalar value from Series or scalar
    def get_scalar(value):
        if isinstance(value, pd.Series):
            return value.iloc[0] if len(value) > 0 else value.item()
        return value

    close_price = get_scalar(latest_data['Close'])
    sma_50 = get_scalar(latest_data[f'SMA_{SMA_SHORT}'])
    sma_100 = get_scalar(latest_data[f'SMA_{SMA_MEDIUM}'])
    sma_200 = get_scalar(latest_data[f'SMA_{SMA_LONG}'])

    # Strong Bullish Stack (Sell Signal based on strategy's defined exit point)
    # Price > SMA(50) > SMA(100) > SMA(200)
    sell_condition = (close_price > sma_50) and \
                     (sma_50 > sma_100) and \
                     (sma_100 > sma_200)

    # Strong Bearish Stack (Buy Signal based on strategy's defined entry point)
    # Price < SMA(50) < SMA(100) < SMA(200)
    buy_condition = (close_price < sma_50) and \
                    (sma_50 < sma_100) and \
                    (sma_100 < sma_200)

    if buy_condition:
        print("SIGNAL: ESTABLISHED BUY (Strong Bearish Stack)")
        print("Status: Price and SMAs are perfectly stacked (P < 50 < 100 < 200), confirming a strong downtrend. This is your specified *Buy Entry* point.")
    elif sell_condition:
        print("SIGNAL: ESTABLISHED SELL (Strong Bullish Stack)")
        print("Status: Price and SMAs are perfectly stacked (P > 50 > 100 > 200), confirming a strong uptrend. This is your specified *Sell/Exit* point.")
    else:
        print("NO STACKING SIGNAL: Averages are not in the perfect configuration.")


def check_anticipatory_signal(data: pd.DataFrame):
    """
    Checks for a potential trend reversal using MACD and SMA 50 crossover.
    Requires at least the last two trading days for checking crossovers.
    """
    if len(data) < 2:
        return

    # Get the data for the last two days
    latest = data.iloc[-1]
    previous = data.iloc[-2]

    # Helper function to get scalar value from Series or scalar
    def get_scalar(value):
        if isinstance(value, pd.Series):
            return value.iloc[0] if len(value) > 0 else value.item()
        return value

    # Crossover: Price crossing the SMA 50
    # Price crossing ABOVE SMA 50
    cross_above_50 = (get_scalar(latest['Close']) > get_scalar(latest[f'SMA_{SMA_SHORT}'])) and \
                     (get_scalar(previous['Close']) <= get_scalar(
                         previous[f'SMA_{SMA_SHORT}']))

    # Price crossing BELOW SMA 50
    cross_below_50 = (get_scalar(latest['Close']) < get_scalar(latest[f'SMA_{SMA_SHORT}'])) and \
                     (get_scalar(previous['Close']) >= get_scalar(
                         previous[f'SMA_{SMA_SHORT}']))

    # Momentum Confirmation: MACD crossing its Signal Line
    # MACD crossing ABOVE Signal Line (Bullish Momentum)
    macd_cross_up = (get_scalar(latest['MACD']) > get_scalar(latest['MACD_Signal'])) and \
                    (get_scalar(previous['MACD']) <=
                     get_scalar(previous['MACD_Signal']))

    # MACD crossing BELOW Signal Line (Bearish Momentum)
    macd_cross_down = (get_scalar(latest['MACD']) < get_scalar(latest['MACD_Signal'])) and \
                      (get_scalar(previous['MACD']) >=
                       get_scalar(previous['MACD_Signal']))

    print("\n--- MACD Momentum Analysis ---")

    # Anticipatory Buy Signal (MACD confirmed crossover with Price/SMA 50 cross)
    if cross_above_50 and macd_cross_up:
        print("ANT: POTENTIAL BUY SIGNAL (Crossover Confirmed)")
        print("Reason: Price crossed above SMA 50 AND MACD just crossed its Signal Line (Bullish Momentum).")
        print("Action: Consider a 'wait' period for 1-2 more days to confirm follow-through, or initiate a partial 'Buy' position.")

    # Anticipatory Sell Signal (MACD confirmed crossover with Price/SMA 50 cross)
    elif cross_below_50 and macd_cross_down:
        print("ANT: POTENTIAL SELL SIGNAL (Crossover Confirmed)")
        print("Reason: Price crossed below SMA 50 AND MACD just crossed its Signal Line (Bearish Momentum).")
        print("Action: Consider a 'wait' period for 1-2 more days to confirm follow-through, or initiate a partial 'Sell/Exit' position.")

    # Momentum Divergence - MACD and Price/SMA50 mismatch
    elif cross_above_50 and macd_cross_down:
        print("ANT: DIVERGENCE WARNING (Price vs. Momentum)")
        print("Reason: Price crossed bullishly above SMA 50, but MACD just turned bearish. Caution is advised. 'Wait' for clearer confirmation.")

    elif cross_below_50 and macd_cross_up:
        print("ANT: DIVERGENCE WARNING (Price vs. Momentum)")
        print("Reason: Price crossed bearishly below SMA 50, but MACD just turned bullish. Caution is advised. 'Wait' for clearer confirmation.")

    else:
        print("NO ANTICIPATORY SIGNAL: No combined MACD/SMA 50 crossover detected.")

    # Print MACD details for context
    macd_val = get_scalar(latest['MACD'])
    macd_signal_val = get_scalar(latest['MACD_Signal'])
    close_val = get_scalar(latest['Close'])
    sma_50_val = get_scalar(latest[f'SMA_{SMA_SHORT}'])

    print(f"\nLatest MACD:       {macd_val:.2f}")
    print(f"Latest MACD Signal: {macd_signal_val:.2f}")
    print(f"Latest Price vs SMA 50: {close_val:.2f} vs {sma_50_val:.2f}")
    print("-" * 30)


def analyze_stock(ticker_symbol: str, period: str = "1y"):
    """Main function to run the full analysis."""
    print(f"*** Analyzing {ticker_symbol} (Period: {period}) ***")

    # 1. Fetch Data
    try:
        data = yf.download(ticker_symbol, period=period,
                           interval='1d', progress=False, auto_adjust=False)
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return

    # Flatten MultiIndex columns if they exist (yfinance sometimes returns MultiIndex)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    # Check if data is sufficient
    if data.empty or len(data) < SMA_LONG:
        print(
            f"Insufficient data retrieved for {ticker_symbol} (Need at least {SMA_LONG} data points).")
        print("-" * 40)
        return

    # 2. Calculate Indicators
    data = calculate_technical_indicators(data)
    latest_data = data.iloc[-1]

    # Helper function to get scalar value from Series or scalar
    def get_scalar(value):
        if isinstance(value, pd.Series):
            return value.iloc[0] if len(value) > 0 else value.item()
        return value

    # 3. Print Latest Metrics
    close_price = get_scalar(latest_data['Close'])
    sma_50_val = get_scalar(latest_data[f'SMA_{SMA_SHORT}'])
    sma_100_val = get_scalar(latest_data[f'SMA_{SMA_MEDIUM}'])
    sma_200_val = get_scalar(latest_data[f'SMA_{SMA_LONG}'])

    print(f"Date: {latest_data.name.strftime('%Y-%m-%d')}")
    print(f"Close Price: Rs {close_price:.2f}")
    print(f"SMA 50:      Rs {sma_50_val:.2f}")
    print(f"SMA 100:     Rs {sma_100_val:.2f}")
    print(f"SMA 200:     Rs {sma_200_val:.2f}")
    print("-" * 30)

    # 4. Check Signals
    check_sma_stacking_signal(latest_data)
    check_anticipatory_signal(data)

    print("\n" * 2)


if __name__ == '__main__':
    # --- Stock List Configuration ---
    # NOTE: All NSE symbols MUST have the '.NS' suffix for yfinance.
    stocks_to_check = [
        "TCS.NS",
        "IRCTC.NS",
        "NESTLEIND.NS",
        "SBIN.NS",
        "STERTOOLS.NS",
        "ITC.NS",
        "HDFCBANK.NS",
        "BRITANNIA.NS",
        "M&M.NS",
        "PARTYCRUS-SM.NS",
        "BAJAJFINSV.NS",
        "BECTORFOOD.NS",
        "YESBANK.NS",
        "LGEINDIA.NS",
        "TATACAP.NS",
        "DRREDDY.NS",
        "RECLTD.NS",
        "ITDC.NS",
        "INDHOTEL.NS",
        "PFC.NS",
        "JKIL.NS",
        "SUZLON.NS",
        "EIHAHOTELS.NS",
        "TATAPOWER.NS",
        "RPOWER.NS",
        "IIFL.NS",
        "PAYTM.NS",
        "SWSOLAR.NS",
        "TATAELXSI.NS",
        "PATELENG.NS",
        "PRECAM.NS",
        "LYKALABS.NS",
        "UJJIVANSFB.NS",
        "ETERNAL.NS",
        "JIOFIN.NS",
        "REFEX.NS",
        "ZAGGLE.NS"
    ]
    # Set the historical period for fetching data (e.g., '1y', '2y', '5y')
    DATA_PERIOD = '2y'
    # ------------------------------

    # Run analysis for each stock
    for stock in stocks_to_check:
        analyze_stock(stock, period=DATA_PERIOD)

    print("--- FULL ANALYSIS COMPLETE ---")
