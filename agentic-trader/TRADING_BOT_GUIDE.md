# Automated Trading Bot - Setup & Usage Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root with the following:

```env
# KiteConnect API Credentials
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
KITE_ACCESS_TOKEN=your_access_token

# AI Provider API Keys
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
HUGGINGFACEHUB_API_TOKEN=your_hf_token  # Optional

# LangSmith (Optional - for tracing)
LANGSMITH_API_KEY=your_langsmith_key
```

### 3. Run the Trading Bot

#### Test Mode (Single Run)
```bash
python main.py test
```

#### Production Mode (Runs Every 15 Minutes)
```bash
python main.py
```

## 📋 Features

### Core Functionality
- **Automated Trading**: Runs every 15 minutes during market hours
- **Multi-Strategy Analysis**: Uses 5 different trading strategies
- **AI-Powered Decisions**: LLM-based trade confirmation
- **Risk Management**: Stop loss, position sizing, and portfolio limits
- **Comprehensive Logging**: All decisions and trades are logged

### Trading Strategies
1. **Moving Average Crossover**: Trend following
2. **RSI Strategy**: Momentum based
3. **Bollinger Bands**: Mean reversion
4. **Supertrend**: Trend + volatility
5. **AI Strategy**: LLM-powered analysis

### Safety Features
- Maximum 5 concurrent positions
- Maximum 20% capital per trade
- 2% stop loss protection
- 5% profit target
- Volume and price filters

## ⚙️ Configuration

Edit the configuration in `main.py`:

```python
TRADING_CONFIG = {
    'max_positions': 5,              # Maximum concurrent positions
    'max_capital_per_trade': 0.2,    # 20% of capital per trade
    'stop_loss_percent': 0.02,       # 2% stop loss
    'target_percent': 0.05,           # 5% target
    'min_volume': 100000,             # Minimum volume filter
    'min_price': 50,                  # Minimum price (₹)
    'max_price': 5000,                # Maximum price (₹)
    'enable_real_trading': False,     # Set True for real trading
    'use_ai_confirmation': True,      # Use AI for confirmation
}
```

## 🔄 How It Works

### Trading Cycle (Every 15 Minutes)
1. **Market Check**: Verifies if market is open (9:15 AM - 3:30 PM IST, weekdays)
2. **Stock Selection**: Fetches top 50 stocks by volume from NSE
3. **Filtering**: Applies price, volume, and position filters
4. **Analysis**: Runs 5 strategies on each selected stock
5. **Decision Making**: Calculates ensemble signal with weighted voting
6. **AI Confirmation**: Gets LLM-based trade confirmation
7. **Order Execution**: Places buy/sell orders based on signals
8. **Risk Management**: Monitors stop loss and targets
9. **Logging**: Records all decisions and trades

### Signal Generation
- **BUY Signal**: When >50% of weighted strategies signal BUY
- **SELL Signal**: When >50% of weighted strategies signal SELL
- **HOLD Signal**: Default when no clear consensus

### Position Management
- Tracks all open positions in `out/logs/positions.json`
- Automatically exits on stop loss (2%) or target (5%)
- Closes positions when SELL signal is generated

## 📊 Monitoring

### Log Files
- **Trading Log**: `out/logs/trading_YYYYMMDD.log`
- **Trade Decisions**: `out/logs/trade_decisions.jsonl`
- **Positions**: `out/logs/positions.json`

### Real-time Monitoring
```bash
# Watch trading log
tail -f out/logs/trading_$(date +%Y%m%d).log

# Monitor positions
watch -n 60 cat out/logs/positions.json
```

## 🚨 Important Notes

### Testing vs Production
- **Default Mode**: SIMULATED trading (no real orders)
- **Enable Real Trading**: Set `enable_real_trading: True` in config
- **Test First**: Always test in simulated mode before real trading

### Rate Limiting
- Built-in delays between API calls
- Processes maximum 10 stocks per cycle
- 2-second delay between stock analyses

### Market Hours
- Only trades during NSE market hours
- Weekdays: 9:15 AM - 3:30 PM IST
- Skips weekends and holidays

## 🛡️ Risk Management

### Capital Protection
- Never uses more than 20% capital per trade
- Maximum 5 concurrent positions
- Automatic stop loss at 2%

### Position Sizing
```python
position_size = min(
    available_capital,
    total_capital * 0.20  # 20% max
) / stock_price
```

## 🔧 Troubleshooting

### Common Issues

1. **KiteConnect Authentication Error**
   - Regenerate access token
   - Update `.env` file
   - Check API limits

2. **No Stocks Found**
   - Check market hours
   - Verify NSE connection
   - Review filters in config

3. **Strategy Errors**
   - Check historical data availability
   - Verify strategy implementations
   - Review error logs

### Debug Mode
```bash
# Run with detailed logging
python -u main.py test 2>&1 | tee debug.log
```

## 📈 Performance Tracking

### Daily Summary
The bot prints a summary after each cycle:
- Active positions and entry prices
- Today's trade count
- Total P&L for the day

### Analysis Scripts
```python
# Analyze trade history
python src/agentic-trader/analyze_log.py

# Benchmark strategies
python src/agentic-trader/benchmark.py
```

## ⚠️ Disclaimer

**IMPORTANT**: This is an automated trading system. Please note:
- Trading involves substantial risk of loss
- Past performance doesn't guarantee future results
- Always test thoroughly before real trading
- Monitor the system regularly
- Have manual override capabilities
- Never invest more than you can afford to lose

## 🆘 Support

### Logs to Check
1. Main trading log: `out/logs/trading_YYYYMMDD.log`
2. Trade decisions: `out/logs/trade_decisions.jsonl`
3. Console output for real-time updates

### Manual Override
To stop the bot immediately:
- Press `Ctrl+C` in the terminal
- The bot will complete the current cycle and exit gracefully

## 🔄 Updates & Maintenance

### Regular Tasks
- Review and update strategy parameters weekly
- Check log files for errors daily
- Update stock filters based on market conditions
- Regenerate KiteConnect access token as needed

### Backup
Regularly backup:
- `out/logs/` directory
- `.env` file
- `positions.json`

---

**Remember**: Always start with paper trading and thoroughly test the system before enabling real trading!