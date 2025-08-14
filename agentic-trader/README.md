# Agentic Trader 🤖📈

A sophisticated algorithmic trading system that combines traditional technical analysis strategies with AI-powered decision making for automated stock trading.

## 🚀 Features

- **Multiple Trading Strategies**: Bollinger Bands, Moving Average Crossover, RSI, Supertrend, and AI-based strategies
- **Backtesting Engine**: Comprehensive historical performance analysis with detailed metrics
- **AI Integration**: LLM-powered decision making using Groq and OpenAI
- **Real-time Data**: Live market data integration via KiteConnect
- **Risk Management**: Built-in position sizing and risk controls
- **Performance Analytics**: Win rate, drawdown, and P&L analysis
- **Rate Limiting**: Intelligent API rate limiting to prevent KiteConnect throttling

## 🏗️ Architecture

```
agentic-trader/
├── strategy/                 # Trading strategy implementations
│   ├── base_strategy.py     # Base strategy class
│   ├── bb_strategy.py       # Bollinger Bands strategy
│   ├── ma_crossover_strategy.py  # Moving Average Crossover
│   ├── rsi_strategy.py      # RSI strategy
│   ├── supertrend_strategy.py    # Supertrend indicator
│   └── ai_strategy.py       # AI-powered strategy
├── app/                     # Web application
├── notebooks/               # Jupyter notebooks for analysis
├── backtest_runner.py       # Backtesting engine
├── decision_chain.py        # AI decision pipeline
├── kite_connect.py          # Market data integration
└── utility.py               # Helper functions
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- KiteConnect API credentials
- Groq or OpenAI API key (for AI strategies)

### Setup

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd agentic-trader
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   ```bash
   # Set environment variables or create config file
   export KITE_API_KEY="your_kite_api_key"
   export GROQ_API_KEY="your_groq_api_key"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

## 📊 Trading Strategies

### 1. **Bollinger Bands Strategy**

- Uses Bollinger Bands for entry/exit signals
- Configurable standard deviation and period
- Mean reversion approach

### 2. **Moving Average Crossover**

- Fast and slow moving average crossover signals
- Trend-following strategy
- Customizable periods

### 3. **RSI Strategy**

- Relative Strength Index based signals
- Overbought/oversold conditions
- Configurable thresholds

### 4. **Supertrend Strategy**

- Supertrend indicator for trend following
- ATR-based stop losses
- Momentum-based entries

### 5. **AI Strategy**

- LLM-powered market analysis
- Natural language signal generation
- Adaptive decision making

## 🔄 Backtesting

### Run Backtests

```python
from backtest_runner import BacktestRunner
from strategy.bb_strategy import BollingerBandsStrategy

# Initialize backtest runner
runner = BacktestRunner(
    strategy_cls=BollingerBandsStrategy,
    capital=100000
)

# Run backtest
results = runner.run("RELIANCE", historical_data)
print(f"Total P&L: {results['total_pnl']}")
print(f"Win Rate: {results['win_rate_percent']}%")
```

### Performance Metrics

- **Total P&L**: Overall profit/loss
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest peak-to-trough decline
- **Average P&L per Trade**: Mean trade performance
- **Trade Count**: Total number of executed trades

## 🤖 AI Integration

### Decision Chain

```python
from decision_chain import run_agent

# Get AI-powered trading decision
decision = run_agent(
    ohlc_data,
    volume_data,
    provider="groq"  # or "openai"
)
```

### Supported LLM Providers

- **Groq**: Fast inference, cost-effective
- **OpenAI**: High-quality analysis, GPT models

## 📈 Live Trading

### Market Data

```python
from kite_connect import fetch_historical, fetch_top_volume

# Get historical data
data = fetch_historical("RELIANCE", interval='5minute', duration='5d')

# Get top volume stocks
top_stocks = fetch_top_volume(index_nifty='', size=50)
```

### Rate Limiting

The system includes intelligent rate limiting to prevent KiteConnect API throttling:

- Automatic delays between API calls
- Retry logic for failed requests
- Configurable rate limits

## 📱 Web Interface

### Start the Application

```bash
cd app
python app.py
```

Access the web interface at `http://localhost:5000`

### Features

- Real-time strategy performance
- Trade execution interface
- Portfolio monitoring
- Strategy backtesting UI

## 📊 Analysis Tools

### Log Analysis

```python
from analyze_log import analyze_log

# Analyze trading performance
analysis = analyze_log()
```

### Benchmark Testing

```python
from benchmark import benchmark_stocks

# Test multiple strategies on multiple stocks
results = benchmark_stocks(["RELIANCE", "TCS", "HDFCBANK"])
```

## ⚙️ Configuration

### Rate Limiting Settings

```python
# config.py
API_DELAY = 1.0          # Delay between API calls
MAX_RETRIES = 3          # Maximum retry attempts
RETRY_DELAY = 5.0        # Delay before retries
```

### Strategy Parameters

```python
# Customize strategy parameters
strategy = BollingerBandsStrategy(
    capital=100000,
    bb_period=20,
    bb_std=2.0
)
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python test_strategies.py

# Test rate limiting
python test_rate_limiting.py
```

### Test Coverage

- Strategy implementations
- Backtesting engine
- API integrations
- Error handling

## 📝 Logging

### Log Files

- `out/logs/trade_decisions.jsonl`: Trading decisions
- `out/logs/trades_log.json`: Trade execution logs

### Log Levels

- **INFO**: General information and progress
- **WARNING**: Rate limit warnings
- **ERROR**: API failures and errors

## 🚨 Error Handling

### Common Issues

1. **Rate Limiting**: Automatic retry with exponential backoff
2. **API Failures**: Graceful degradation and logging
3. **Data Issues**: Validation and error reporting

### Troubleshooting

```bash
# Check logs for errors
tail -f out/logs/trade_decisions.jsonl

# Test API connectivity
python test_kite_connect.py
```

## 🔒 Risk Management

### Position Sizing

- Capital-based position sizing
- Risk per trade limits
- Portfolio diversification

### Stop Losses

- ATR-based stop losses
- Trailing stops
- Maximum loss limits

## 📈 Performance Optimization

### Best Practices

1. **Batch Operations**: Group API calls to minimize delays
2. **Caching**: Cache frequently accessed data
3. **Parallel Processing**: Process multiple symbols concurrently
4. **Memory Management**: Stream large datasets

### Monitoring

- Real-time performance metrics
- API usage statistics
- Error rate monitoring

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Add type hints where appropriate
- Include docstrings for functions
- Write comprehensive tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**This software is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.**

## 🆘 Support

### Documentation

- [Rate Limiting Guide](RATE_LIMITING_README.md)
- [Strategy Development Guide](docs/strategy_development.md)
- [API Reference](docs/api_reference.md)

### Issues

- Report bugs via GitHub Issues
- Request features via GitHub Discussions
- Ask questions in the community forum

### Community

- Join our Discord server
- Follow updates on Twitter
- Subscribe to our newsletter

---

**Built with ❤️ for the trading community**

_Last updated: December 2024_
