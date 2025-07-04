from kite_connect import fetch_quote, fetch_historical, fetch_top_volume
from decision_chain import run_agent
from backtest_runner import BacktestRunner
from strategy.supertrend_strategy import SupertrendStrategy
from strategy.bb_strategy import BollingerBandsStrategy
from strategy.ma_crossover_strategy import MovingAverageCrossoverStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.ai_strategy import AIBasedStrategy
from analyze_log import log_trade_decision_json
import json
import datetime
import random

exchange = "NSE"


def get_decision_history(log_path: str = "logs/trade_decisions.jsonl"):
    with open(log_path) as f:
        data = json.load(f)
    return data


def log_decision_index(index: str = "", size=50, sample_size=10):
    top_traded = fetch_top_volume(exchange=exchange, index_nifty=index)

    for data in top_traded[:sample_size]:
        symbol = data['symbol']
        ohlc = data['ohlc']
        volume = data["volume"]
        decision = run_agent(ohlc, volume, provider="groq")  # or "openai"
        log = {
            "timestamp": datetime.datetime.now().isoformat(),
            "symbol": symbol,
            "instrument_token": data['token'],
            "last_price": data['last_price'],
            "ohlc": ohlc,
            "volume": volume,
            "decision": decision
        }

        log_trade_decision_json(log)


def backtest_strategy(strategy_cls, amount, symbols: list):
    decisions = []
    runner = BacktestRunner(strategy_cls=strategy_cls, capital=amount)
    for symbol in symbols:
        historical_data = fetch_historical(symbol)
        if historical_data and len(historical_data) > 0:
            print(f"records {symbol}: {len(historical_data)}")
            decision = runner.run(symbol, historical_data=historical_data)
            decisions.append((symbol, decision))
        else:
            print(f"No data found for {symbol}")

    return decisions


def main():
    strategy_cls = [AIBasedStrategy, BollingerBandsStrategy,
                    MovingAverageCrossoverStrategy, SupertrendStrategy, RSIStrategy]
    indexes = ['', 'next', 'midcap', 'smallcap']
    for cls in strategy_cls:
        index = random.choice(indexes)
        top50_list = fetch_top_volume(
            exchange=exchange, index_nifty=index, size=50)
        symbols = [item['symbol'] for item in top50_list]
        decisions = backtest_strategy(cls, 15000, symbols)
        if len(decisions) > 0:
            log_trade_decision_json(
                decisions, f"logs/{cls.__name__}_{index}_decisions.jsonl")


if __name__ == "__main__":
    main()
