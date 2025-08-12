from unittest import TestCase
from kite_connect import fetch_historical, fetch_top_volume
from decision_chain import run_agent
from backtest_runner import BacktestRunner
from strategy.supertrend_strategy import SupertrendStrategy
from strategy.bb_strategy import BollingerBandsStrategy
from strategy.ma_crossover_strategy import MovingAverageCrossoverStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.ai_strategy import AIBasedStrategy
from analyze_log import log_trade_decision_json
from utility import validate_json_structure
from benchmark import benchmark_stocks

import json
import datetime
import random
import time
import logging
from config import API_DELAY, MAX_RETRIES, RETRY_DELAY, EXCHANGE, LOG_LEVEL, LOG_FORMAT

# Set up logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

exchange = EXCHANGE


def safe_api_call(func, *args, **kwargs):
    """
    Wrapper function to handle API calls with rate limiting and retries
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = func(*args, **kwargs)
            time.sleep(API_DELAY)  # Rate limiting delay
            return result
        except Exception as e:
            if "Too many requests" in str(e) or "rate limit" in str(e).lower():
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"Rate limit hit, waiting {RETRY_DELAY} seconds before retry {attempt + 1}/{MAX_RETRIES}")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    logger.error(f"Max retries reached for rate limit: {e}")
                    return None
            else:
                logger.error(f"API call failed: {e}")
                return None
    return None


def get_decision_history(log_path: str = "out/logs/trade_decisions.jsonl"):
    """
    Safely loads decision history with validation.
    """
    try:
        # For JSONL files, we need to read line by line
        decisions = []
        with open(log_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                try:
                    decision = json.loads(line)
                    # Validate decision structure
                    required_keys = ['timestamp', 'symbol', 'decision']
                    is_valid, error_msg = validate_json_structure(
                        decision, required_keys=required_keys)

                    if is_valid:
                        decisions.append(decision)
                    else:
                        print(
                            f"Warning: Invalid decision on line {line_num}: {error_msg}")

                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue

        return decisions
    except FileNotFoundError:
        print(f"Decision history file not found: {log_path}")
        return []
    except Exception as e:
        print(f"Error loading decision history: {e}")
        return []


def log_decision_index(index: str = "", size=50, sample_size=10):
    top_traded = safe_api_call(
        fetch_top_volume, exchange=exchange, index_nifty=index)
    if not top_traded:
        logger.error(f"Failed to fetch top volume data for index {index}")
        return

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
        historical_data = safe_api_call(
            fetch_historical, symbol, interval='15minute', duration='5d')
        if historical_data and len(historical_data) > 0:
            print(f"records {symbol}: {len(historical_data)}")
            decision = runner.run(
                symbol=symbol, historical_data=historical_data)
            if decision and decision['total_trades'] > 0:
                decisions.append((symbol, decision))
            else:
                print(f"No trades executed for {symbol}")
        else:
            print(f"No data found for {symbol}")

    return decisions


def random_n(items: list[str], size=10) -> list:
    return random.sample([item['symbol']
                          for item in items], min(size, len(items)))


def run_backtest_top10():
    strategy_cls = [BollingerBandsStrategy,
                    MovingAverageCrossoverStrategy, RSIStrategy]
    # , SupertrendStrategy, AIBasedStrategy]
    indexes = ['', 'next', 'midcap', 'smallcap']
    for cls in strategy_cls:
        index = random.choice(indexes)
        top50_list = safe_api_call(
            fetch_top_volume, exchange=exchange, index_nifty=index, size=50)
        if not top50_list:
            logger.error(f"Failed to fetch top volume data for index {index}")
            continue

        symbols = random_n(top50_list)
        decisions = backtest_strategy(cls, 15000, symbols)
        print(f"{cls.__name__}: decisions: {len(decisions)}")
        if len(decisions) > 0:
            print(f"Trade decision {len(symbols)}: {len(decisions)}")
            # Log each decision individually since decisions is a list of tuples
            for symbol, decision in decisions:
                log_trade_decision_json(
                    decision, f"logs/{cls.__name__}_{index}_decisions.jsonl")


def my_main():
    logger.info("Starting data collection from multiple indices...")

    # Fetch data from indices with delays to avoid rate limits
    index_smallcap = safe_api_call(
        fetch_top_volume, index_nifty='smallcap', size=50)
    if index_smallcap:
        logger.info(f"Fetched {len(index_smallcap)} smallcap stocks")

    index_midcap = safe_api_call(
        fetch_top_volume, index_nifty='midcap', size=50)
    if index_midcap:
        logger.info(f"Fetched {len(index_midcap)} midcap stocks")

    index_next = safe_api_call(fetch_top_volume, index_nifty='next', size=50)
    if index_next:
        logger.info(f"Fetched {len(index_next)} next50 stocks")

    index_large = safe_api_call(fetch_top_volume, index_nifty='', size=50)
    if index_large:
        logger.info(f"Fetched {len(index_large)} large cap stocks")

    # Flatten the results into a single list
    trade_decisions = []

    if index_smallcap:
        trade_decisions.extend(benchmark_stocks(random_n(index_smallcap)))
        logger.info("Completed smallcap benchmark")

    if index_midcap:
        trade_decisions.extend(benchmark_stocks(random_n(index_midcap)))
        logger.info("Completed midcap benchmark")

    if index_next:
        trade_decisions.extend(benchmark_stocks(random_n(index_next)))
        logger.info("Completed next50 benchmark")

    if index_large:
        trade_decisions.extend(benchmark_stocks(random_n(index_large)))
        logger.info("Completed large cap benchmark")

    logger.info(f"Total trade decisions collected: {len(trade_decisions)}")
    return trade_decisions


class StrategiesTestCase(TestCase):
    def test_my_main(self):
        decisions = my_main()
        self.assertGreater(len(decisions), 0)

    def test_trad_decisions(self):
        trade_decisions = my_main()
        print("~~~~~~~~~~~~~~~~~~~~~ trade decisions ~~~~~~~~~~~~~~~~~~~~~~~~\n")
        print(trade_decisions)
        print("\n~~~~~~~~~~~~~~~~~~~~~ trade decisions ~~~~~~~~~~~~~~~~~~~~~~~~")
        # Log each trade decision individually since they're now separate dictionaries
        for decision in trade_decisions:
            log_trade_decision_json(decision)
