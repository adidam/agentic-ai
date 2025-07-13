from strategy.ai_strategy import AIBasedStrategy
from strategy.bb_strategy import BollingerBandsStrategy
from strategy.ma_crossover_strategy import MovingAverageCrossoverStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.supertrend_strategy import SupertrendStrategy
from kite_connect import fetch_historical
from backtest_runner import BacktestRunner

strategies = [AIBasedStrategy, BollingerBandsStrategy, MovingAverageCrossoverStrategy,
              SupertrendStrategy, RSIStrategy]
securities = ["INFY", "TCS", "HDFCBANK", "RELIANCE"]


def benchmark_stocks(symbols: list[str] = securities) -> list:
    benchmark_results = []

    for strategy in strategies:
        for symbol in symbols:
            data = fetch_historical(symbol, interval='5minute', duration='5d')
            if data and len(data) > 0:
                runner = BacktestRunner(strategy, capital=15000)
                result = runner.run(symbol=symbol, historical_data=data)
                benchmark_results.append({
                    "strategy": strategy.__name__,
                    "symbol": symbol,
                    "total_pnl": result["total_pnl"],
                    "win_rate": result["win_rate_percent"],
                    "drawdown": result.get("max_drawdown", 0),
                    "trades": result["trades"]
                })
            else:
                print(f"Ignored symbol {symbol}")

    return benchmark_results
