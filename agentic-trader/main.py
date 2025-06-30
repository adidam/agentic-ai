from kite_connect import fetch_quote, is_valid_symbol, list_symbols, fetch_historical
from decision_chain import run_agent
from backtest_runner import BacktestRunner
from strategy.supertrend_strategy import SupertrendStrategy
import json
import datetime


def get_decision_history(log_path: str = "logs/trad_log_2025-06-15"):
    with open(log_path) as f:
        data = json.load(f)
    return data


def main():
    exchange = "NSE"

    print(list_symbols(exchange=exchange))
    symbol = input("Symbol enti: ")

    ex_sym = f"{exchange}:{symbol}"
    instument = is_valid_symbol(symbol, exchange)
    print(f"instument: {instument}")

    if not instument:
        print("invalid symbol {}", ex_sym)
        exit(1)

    data = fetch_quote(symbol=symbol, exchange=exchange)
    print(f"Quote: {data}")
    ohlc = data['ohlc']
    volume = data["volume"]

    decision = run_agent(ohlc, volume, provider="groq")  # or "openai"

    log = {
        "timestamp": datetime.datetime.now().isoformat(),
        "ohlc": ohlc,
        "volume": volume,
        "decision": decision
    }

    print(json.dumps(log, indent=2))
    # Add order logic here if you trust the decision
    runner = BacktestRunner(SupertrendStrategy, 10000)
    historical_data = fetch_historical(symbol)
    print(f"records: {len(historical_data)}")
    runner.run(symbol, historical_data=historical_data)


if __name__ == "__main__":
    main()
