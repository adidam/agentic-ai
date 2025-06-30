from strategy.ma_crossover_strategy import MovingAverageCrossoverStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.ai_strategy import AIBasedStrategy
from strategy.bb_strategy import BollingerBandsStrategy

from backtest_runner import BacktestRunner

# Suppose historical_data is already fetched via Kite
runner = BacktestRunner(MovingAverageCrossoverStrategy,
                        capital=10000, short_window=10, long_window=50)
result = runner.run(historical_data)

print("📊 Backtest Summary:")
print(result["total_trades"], "trades")
print("Total PnL:", result["total_pnl"])
print("Win rate:", result["win_rate_percent"], "%")

runner = BacktestRunner(BollingerBandsStrategy,
                        capital=10000, period=20, deviation=2)
result = runner.run(historical_data)
print(result)
