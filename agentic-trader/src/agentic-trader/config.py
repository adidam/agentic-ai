"""
Configuration file for API rate limiting and other settings
"""

# API Rate Limiting Settings
API_DELAY = 1.0  # Delay between API calls in seconds
MAX_RETRIES = 3  # Maximum number of retries for failed API calls
RETRY_DELAY = 5.0  # Delay before retrying after rate limit error

# KiteConnect Settings
EXCHANGE = "NSE"
DEFAULT_CAPITAL = 15000

# Data Fetching Settings
HISTORICAL_INTERVAL = '5minute'
HISTORICAL_DURATION = '5d'
TOP_VOLUME_SIZE = 50

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File Paths
LOG_DIR = "out/logs"
TRADE_DECISIONS_FILE = "out/logs/trade_decisions.jsonl"
TRADES_LOG_FILE = "out/logs/trades_log.json"
