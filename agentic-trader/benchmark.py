from strategy.ai_strategy import AIBasedStrategy
from strategy.bb_strategy import BollingerBandsStrategy
from strategy.ma_crossover_strategy import MovingAverageCrossoverStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.supertrend_strategy import SupertrendStrategy
strategies = [RSIStrategy, MovingAverageCrossoverStrategy,
              BollingerBandsStrategy, AIBasedStrategy, SupertrendStrategy]
securities = ["NSE:INFY", "NSE:TCS", "NSE:HDFCBANK", "NSE:RELIANCE"]

benchmark_results = []

for strategy in strategies:
    for symbol in securities:
        data = fetch_historical(symbol)
        runner = BacktestRunner(strategy, capital=10000)
        result = runner.run(data)
        benchmark_results.append({
            "strategy": strategy.__name__,
            "symbol": symbol,
            "total_pnl": result["total_pnl"],
            "win_rate": result["win_rate_percent"],
            "drawdown": result.get("max_drawdown", 0),
            "trades": result["trades"]
        })
