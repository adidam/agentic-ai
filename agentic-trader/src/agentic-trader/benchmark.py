from strategy.ai_strategy import AIBasedStrategy
from strategy.bb_strategy import BollingerBandsStrategy
from strategy.ma_crossover_strategy import MovingAverageCrossoverStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.supertrend_strategy import SupertrendStrategy
from kite_connect import fetch_historical
from backtest_runner import BacktestRunner
import time
import logging
from config import API_DELAY, MAX_RETRIES, RETRY_DELAY, HISTORICAL_INTERVAL, HISTORICAL_DURATION, DEFAULT_CAPITAL

# Set up logging
logger = logging.getLogger(__name__)

strategies = [BollingerBandsStrategy, MovingAverageCrossoverStrategy,
              RSIStrategy]  # SupertrendStrategy,
securities = ["INFY", "TCS", "HDFCBANK", "RELIANCE"]


def safe_fetch_historical(symbol, interval=HISTORICAL_INTERVAL, duration=HISTORICAL_DURATION):
    """
    Wrapper function to handle historical data fetching with rate limiting and retries
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = fetch_historical(
                symbol, interval=interval, duration=duration)
            time.sleep(API_DELAY)  # Rate limiting delay
            return result
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            if "Too many requests" in str(e) or "rate limit" in str(e).lower():
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"Rate limit hit for {symbol}, waiting {RETRY_DELAY} seconds before retry {attempt + 1}/{MAX_RETRIES}")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    logger.error(f"Max retries reached for {symbol}: {e}")
                    return None
            else:
                logger.error(
                    f"Failed to fetch historical data for {symbol}: {e}")
                return None
    return None


def benchmark_stocks(symbols: list[str] = securities) -> list:
    benchmark_results = []
    logger.info(
        f"Starting benchmark for {len(symbols)} symbols with {len(strategies)} strategies")

    for strategy in strategies:
        logger.info(f"Testing strategy: {strategy.__name__}")
        for symbol in symbols:
            logger.info(f"Fetching data for {symbol}")
            data = safe_fetch_historical(
                symbol, interval=HISTORICAL_INTERVAL, duration=HISTORICAL_DURATION)
            if data and len(data) > 0:
                logger.info(
                    f"Running backtest for {symbol} with {strategy.__name__}")
                runner = BacktestRunner(strategy, capital=DEFAULT_CAPITAL)
                result = runner.run(symbol=symbol, historical_data=data)
                benchmark_results.append({
                    "strategy": strategy.__name__,
                    "symbol": symbol,
                    "total_pnl": result["total_pnl"],
                    "win_rate": result["win_rate_percent"],
                    "drawdown": result.get("max_drawdown", 0),
                    "trades": result["trades"]
                })
                logger.info(
                    f"Completed {symbol} with {strategy.__name__}: PnL={result['total_pnl']}, Win Rate={result['win_rate_percent']}%")
            else:
                logger.warning(f"Ignored symbol {symbol} - no data available")

    logger.info(
        f"Benchmark completed. Total results: {len(benchmark_results)}")
    return benchmark_results
