"""
Agentic Trader - Automated Trading System
Runs every 15 minutes to analyze markets and execute trades
"""

import os
import sys
import json
import time
import logging
import schedule
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'agentic-trader'))

# Import trading modules
from kite_session import kite
from kite_connect import fetch_top_volume, fetch_historical, fetch_quote, is_valid_symbol
from nse_top_n import fetch_nifty_top_n_list
from decision_chain import run_agent
from llm_router import get_llm, ask_llm
from utility import safe_json_dump, safe_json_load
from config import (
    DEFAULT_CAPITAL, 
    EXCHANGE, 
    HISTORICAL_INTERVAL, 
    HISTORICAL_DURATION,
    TOP_VOLUME_SIZE,
    LOG_DIR,
    TRADE_DECISIONS_FILE,
    TRADES_LOG_FILE
)

# Import strategies
from strategy.ma_crossover_strategy import MovingAverageCrossoverStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.bb_strategy import BollingerBandsStrategy
from strategy.supertrend_strategy import SupertrendStrategy
from strategy.ai_strategy import AIBasedStrategy

# Load environment variables
load_dotenv(override=True)

# Configure logging
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f'trading_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Trading configuration
TRADING_CONFIG = {
    'max_positions': 5,              # Maximum number of concurrent positions
    'max_capital_per_trade': 0.2,    # Maximum 20% of capital per trade
    'stop_loss_percent': 0.02,       # 2% stop loss
    'target_percent': 0.05,           # 5% target
    'min_volume': 100000,             # Minimum volume filter
    'min_price': 50,                  # Minimum price filter
    'max_price': 5000,                # Maximum price filter
    'enable_real_trading': False,     # Set to True for real trading
    'use_ai_confirmation': True,      # Use AI for trade confirmation
}

# Strategy weights for ensemble decision
STRATEGY_WEIGHTS = {
    'MovingAverageCrossoverStrategy': 0.25,
    'RSIStrategy': 0.20,
    'BollingerBandsStrategy': 0.20,
    'SupertrendStrategy': 0.20,
    'AIBasedStrategy': 0.15,
}

class TradingBot:
    """Main trading bot class that manages the trading workflow"""
    
    def __init__(self, capital: float = DEFAULT_CAPITAL):
        self.capital = capital
        self.positions = {}
        self.pending_orders = {}
        self.today_trades = []
        self.load_positions()
        
    def load_positions(self):
        """Load existing positions from file"""
        positions_file = os.path.join(LOG_DIR, 'positions.json')
        self.positions = safe_json_load(positions_file, default={})
        logger.info(f"Loaded {len(self.positions)} existing positions")
        
    def save_positions(self):
        """Save current positions to file"""
        positions_file = os.path.join(LOG_DIR, 'positions.json')
        safe_json_dump(self.positions, positions_file, indent=2)
        
    def get_available_capital(self) -> float:
        """Calculate available capital for new trades"""
        used_capital = sum(pos['total_cost'] for pos in self.positions.values())
        return self.capital - used_capital
        
    def fetch_market_data(self, symbol: str) -> Optional[Dict]:
        """Fetch current market data for a symbol"""
        try:
            # Add delay to respect rate limits
            time.sleep(1)
            
            # Fetch historical data
            historical = fetch_historical(
                symbol, 
                segment=EXCHANGE,
                interval=HISTORICAL_INTERVAL,
                duration=HISTORICAL_DURATION
            )
            
            if not historical or len(historical) < 60:
                logger.warning(f"Insufficient historical data for {symbol}")
                return None
                
            # Fetch current quote
            quote = fetch_quote(symbol, exchange=EXCHANGE)
            
            return {
                'symbol': symbol,
                'historical': historical,
                'quote': quote,
                'last_price': quote['last_price'],
                'volume': quote['volume'],
                'ohlc': quote['ohlc']
            }
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None
            
    def analyze_with_strategies(self, market_data: Dict) -> Dict:
        """Run multiple strategies and aggregate signals"""
        symbol = market_data['symbol']
        historical = market_data['historical']
        signals = {}
        
        # Initialize strategies
        strategies = {
            'MovingAverageCrossoverStrategy': MovingAverageCrossoverStrategy(self.get_available_capital()),
            'RSIStrategy': RSIStrategy(self.get_available_capital()),
            'BollingerBandsStrategy': BollingerBandsStrategy(self.get_available_capital()),
            'SupertrendStrategy': SupertrendStrategy(self.get_available_capital()),
        }
        
        # Run each strategy
        for name, strategy in strategies.items():
            try:
                result = strategy.run(historical)
                signals[name] = result
                logger.info(f"{symbol} - {name}: {result['signal']} - {result['note']}")
            except Exception as e:
                logger.error(f"Error running {name} for {symbol}: {e}")
                signals[name] = {'signal': 'HOLD', 'size': 0, 'note': f'Error: {e}'}
                
        # Get AI-based signal if configured
        if TRADING_CONFIG['use_ai_confirmation']:
            try:
                ai_decision = self.get_ai_decision(market_data, signals)
                signals['AIBasedStrategy'] = {
                    'signal': ai_decision['action'],
                    'size': 0,
                    'note': ai_decision['reasoning']
                }
            except Exception as e:
                logger.error(f"Error getting AI decision for {symbol}: {e}")
                
        return signals
        
    def get_ai_decision(self, market_data: Dict, strategy_signals: Dict) -> Dict:
        """Get AI-based trading decision"""
        symbol = market_data['symbol']
        
        # Prepare context for AI
        context = {
            'symbol': symbol,
            'last_price': market_data['last_price'],
            'volume': market_data['volume'],
            'ohlc': market_data['ohlc'],
            'strategy_signals': {k: v['signal'] for k, v in strategy_signals.items()},
            'recent_candles': market_data['historical'][-5:]  # Last 5 candles
        }
        
        prompt = f"""
        Analyze the following stock and provide a trading decision:
        
        Symbol: {symbol}
        Current Price: ₹{market_data['last_price']}
        Volume: {market_data['volume']}
        
        Strategy Signals:
        {json.dumps(context['strategy_signals'], indent=2)}
        
        Recent Price Action (last 5 candles):
        {json.dumps(context['recent_candles'], indent=2)}
        
        Based on this data, should we BUY, SELL, or HOLD?
        Provide your decision and a brief reasoning.
        
        Response format:
        DECISION: [BUY/SELL/HOLD]
        REASONING: [Your brief explanation]
        """
        
        try:
            response = ask_llm(prompt, provider="groq", model="llama3-70b-8192")
            
            # Parse response
            lines = response.strip().split('\n')
            decision = 'HOLD'
            reasoning = ''
            
            for line in lines:
                if 'DECISION:' in line:
                    decision = line.split('DECISION:')[1].strip().upper()
                elif 'REASONING:' in line:
                    reasoning = line.split('REASONING:')[1].strip()
                    
            return {
                'action': decision if decision in ['BUY', 'SELL', 'HOLD'] else 'HOLD',
                'reasoning': reasoning or response
            }
            
        except Exception as e:
            logger.error(f"AI decision error: {e}")
            return {'action': 'HOLD', 'reasoning': f'Error: {e}'}
            
    def calculate_ensemble_signal(self, signals: Dict) -> Tuple[str, float]:
        """Calculate weighted ensemble signal from multiple strategies"""
        buy_weight = 0
        sell_weight = 0
        
        for strategy_name, signal_data in signals.items():
            weight = STRATEGY_WEIGHTS.get(strategy_name, 0.1)
            
            if signal_data['signal'] == 'BUY':
                buy_weight += weight
            elif signal_data['signal'] == 'SELL':
                sell_weight += weight
                
        # Determine final signal based on weights
        if buy_weight > 0.5:  # More than 50% weight for BUY
            return 'BUY', buy_weight
        elif sell_weight > 0.5:  # More than 50% weight for SELL
            return 'SELL', sell_weight
        else:
            return 'HOLD', max(buy_weight, sell_weight)
            
    def calculate_position_size(self, symbol: str, price: float) -> int:
        """Calculate position size based on risk management rules"""
        available_capital = self.get_available_capital()
        
        # Apply maximum capital per trade limit
        max_trade_capital = self.capital * TRADING_CONFIG['max_capital_per_trade']
        trade_capital = min(available_capital, max_trade_capital)
        
        # Calculate quantity
        quantity = int(trade_capital / price)
        
        # Apply minimum quantity check
        if quantity < 1:
            return 0
            
        return quantity
        
    def place_order(self, symbol: str, action: str, quantity: int, price: float) -> Dict:
        """Place an order with KiteConnect"""
        try:
            if not TRADING_CONFIG['enable_real_trading']:
                # Simulated order for testing
                order = {
                    'order_id': f"SIM_{datetime.now().timestamp()}",
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': price,
                    'status': 'SIMULATED',
                    'timestamp': datetime.now().isoformat()
                }
                logger.info(f"SIMULATED ORDER: {action} {quantity} shares of {symbol} at ₹{price}")
                return order
                
            # Real order placement (when enabled)
            order_params = {
                'exchange': EXCHANGE,
                'tradingsymbol': symbol,
                'transaction_type': kite.TRANSACTION_TYPE_BUY if action == 'BUY' else kite.TRANSACTION_TYPE_SELL,
                'quantity': quantity,
                'order_type': kite.ORDER_TYPE_LIMIT,
                'price': price,
                'product': kite.PRODUCT_CNC,  # Delivery
                'validity': kite.VALIDITY_DAY
            }
            
            order_id = kite.place_order(**order_params)
            
            order = {
                'order_id': order_id,
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'status': 'PLACED',
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"REAL ORDER PLACED: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order for {symbol}: {e}")
            return {'status': 'FAILED', 'error': str(e)}
            
    def execute_trade_decision(self, symbol: str, market_data: Dict, signals: Dict):
        """Execute trading decision based on signals"""
        # Get ensemble signal
        final_signal, confidence = self.calculate_ensemble_signal(signals)
        
        logger.info(f"{symbol} - Final Signal: {final_signal} (Confidence: {confidence:.2%})")
        
        # Check if we already have a position
        has_position = symbol in self.positions
        
        # Trading logic
        if final_signal == 'BUY' and not has_position:
            # Check if we have room for more positions
            if len(self.positions) >= TRADING_CONFIG['max_positions']:
                logger.info(f"Maximum positions reached. Skipping {symbol}")
                return
                
            # Calculate position size
            quantity = self.calculate_position_size(symbol, market_data['last_price'])
            
            if quantity > 0:
                # Place buy order
                order = self.place_order(symbol, 'BUY', quantity, market_data['last_price'])
                
                if order.get('status') in ['SIMULATED', 'PLACED']:
                    # Update positions
                    self.positions[symbol] = {
                        'quantity': quantity,
                        'entry_price': market_data['last_price'],
                        'total_cost': quantity * market_data['last_price'],
                        'entry_time': datetime.now().isoformat(),
                        'stop_loss': market_data['last_price'] * (1 - TRADING_CONFIG['stop_loss_percent']),
                        'target': market_data['last_price'] * (1 + TRADING_CONFIG['target_percent']),
                        'order_id': order['order_id']
                    }
                    self.save_positions()
                    
                    # Log trade decision
                    self.log_trade_decision(symbol, 'BUY', market_data, signals, order)
                    
        elif final_signal == 'SELL' and has_position:
            # Sell existing position
            position = self.positions[symbol]
            order = self.place_order(symbol, 'SELL', position['quantity'], market_data['last_price'])
            
            if order.get('status') in ['SIMULATED', 'PLACED']:
                # Calculate P&L
                pnl = (market_data['last_price'] - position['entry_price']) * position['quantity']
                pnl_percent = ((market_data['last_price'] - position['entry_price']) / position['entry_price']) * 100
                
                logger.info(f"CLOSING POSITION: {symbol} - P&L: ₹{pnl:.2f} ({pnl_percent:.2f}%)")
                
                # Remove from positions
                del self.positions[symbol]
                self.save_positions()
                
                # Log trade decision
                self.log_trade_decision(symbol, 'SELL', market_data, signals, order, pnl=pnl)
                
        # Check stop loss and target for existing positions
        if has_position:
            self.check_exit_conditions(symbol, market_data)
            
    def check_exit_conditions(self, symbol: str, market_data: Dict):
        """Check stop loss and target conditions for existing positions"""
        position = self.positions.get(symbol)
        if not position:
            return
            
        current_price = market_data['last_price']
        
        # Check stop loss
        if current_price <= position['stop_loss']:
            logger.warning(f"STOP LOSS HIT for {symbol} at ₹{current_price}")
            order = self.place_order(symbol, 'SELL', position['quantity'], current_price)
            
            if order.get('status') in ['SIMULATED', 'PLACED']:
                pnl = (current_price - position['entry_price']) * position['quantity']
                del self.positions[symbol]
                self.save_positions()
                self.log_trade_decision(symbol, 'STOP_LOSS', market_data, {}, order, pnl=pnl)
                
        # Check target
        elif current_price >= position['target']:
            logger.info(f"TARGET HIT for {symbol} at ₹{current_price}")
            order = self.place_order(symbol, 'SELL', position['quantity'], current_price)
            
            if order.get('status') in ['SIMULATED', 'PLACED']:
                pnl = (current_price - position['entry_price']) * position['quantity']
                del self.positions[symbol]
                self.save_positions()
                self.log_trade_decision(symbol, 'TARGET', market_data, {}, order, pnl=pnl)
                
    def log_trade_decision(self, symbol: str, action: str, market_data: Dict, 
                          signals: Dict, order: Dict, pnl: float = None):
        """Log trade decision to file"""
        decision = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'price': market_data['last_price'],
            'volume': market_data['volume'],
            'signals': {k: v['signal'] for k, v in signals.items()},
            'order': order,
            'pnl': pnl
        }
        
        # Append to JSONL file
        with open(TRADE_DECISIONS_FILE, 'a') as f:
            f.write(json.dumps(decision) + '\n')
            
        # Add to today's trades
        self.today_trades.append(decision)
        
    def run_trading_cycle(self):
        """Main trading cycle - runs every 15 minutes"""
        try:
            logger.info("=" * 80)
            logger.info(f"Starting trading cycle at {datetime.now()}")
            logger.info(f"Available Capital: ₹{self.get_available_capital():.2f}")
            logger.info(f"Current Positions: {list(self.positions.keys())}")
            
            # Check if market is open
            if not self.is_market_open():
                logger.info("Market is closed. Skipping trading cycle.")
                return
                
            # Fetch top volume stocks
            logger.info("Fetching top volume stocks...")
            top_stocks = fetch_top_volume(
                exchange=EXCHANGE,
                index_nifty="",
                size=TOP_VOLUME_SIZE
            )
            
            if not top_stocks:
                logger.warning("No stocks fetched. Skipping cycle.")
                return
                
            # Filter stocks based on criteria
            filtered_stocks = self.filter_stocks(top_stocks)
            logger.info(f"Analyzing {len(filtered_stocks)} stocks after filtering")
            
            # Analyze each stock
            for stock_data in filtered_stocks[:10]:  # Limit to top 10 to avoid rate limits
                symbol = stock_data['symbol']
                
                try:
                    logger.info(f"\nAnalyzing {symbol}...")
                    
                    # Fetch market data
                    market_data = self.fetch_market_data(symbol)
                    if not market_data:
                        continue
                        
                    # Run strategies
                    signals = self.analyze_with_strategies(market_data)
                    
                    # Execute trade decision
                    self.execute_trade_decision(symbol, market_data, signals)
                    
                    # Rate limit delay
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    traceback.print_exc()
                    continue
                    
            # Summary
            self.print_summary()
            logger.info("Trading cycle completed")
            
        except Exception as e:
            logger.error(f"Critical error in trading cycle: {e}")
            traceback.print_exc()
            
    def filter_stocks(self, stocks: List[Dict]) -> List[Dict]:
        """Filter stocks based on criteria"""
        filtered = []
        
        for stock in stocks:
            # Apply filters
            if stock['volume'] < TRADING_CONFIG['min_volume']:
                continue
            if stock['last_price'] < TRADING_CONFIG['min_price']:
                continue
            if stock['last_price'] > TRADING_CONFIG['max_price']:
                continue
                
            # Skip if we already have a position
            if stock['symbol'] in self.positions:
                continue
                
            filtered.append(stock)
            
        return filtered
        
    def is_market_open(self) -> bool:
        """Check if market is open for trading"""
        now = datetime.now()
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
            
        # Check market hours (9:15 AM to 3:30 PM IST)
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close
        
    def print_summary(self):
        """Print trading summary"""
        logger.info("\n" + "=" * 80)
        logger.info("TRADING SUMMARY")
        logger.info("=" * 80)
        
        # Current positions
        logger.info(f"Active Positions: {len(self.positions)}")
        for symbol, pos in self.positions.items():
            logger.info(f"  {symbol}: {pos['quantity']} @ ₹{pos['entry_price']:.2f}")
            
        # Today's trades
        logger.info(f"Today's Trades: {len(self.today_trades)}")
        
        # Calculate today's P&L
        today_pnl = sum(t.get('pnl', 0) for t in self.today_trades if t.get('pnl'))
        logger.info(f"Today's P&L: ₹{today_pnl:.2f}")
        
        logger.info("=" * 80)


def run_scheduler():
    """Run the trading bot on schedule"""
    # Initialize trading bot
    bot = TradingBot(capital=DEFAULT_CAPITAL)
    
    # Run immediately on start
    bot.run_trading_cycle()
    
    # Schedule to run every 15 minutes
    schedule.every(15).minutes.do(bot.run_trading_cycle)
    
    logger.info("Trading bot scheduler started. Running every 15 minutes...")
    logger.info("Press Ctrl+C to stop")
    
    # Keep running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)


def test_single_run():
    """Test single run without scheduler"""
    bot = TradingBot(capital=DEFAULT_CAPITAL)
    bot.run_trading_cycle()


if __name__ == "__main__":
    logger.info("Starting Agentic Trader...")
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        logger.info("Running in test mode (single cycle)")
        test_single_run()
    else:
        logger.info("Running in scheduler mode (every 15 minutes)")
        run_scheduler()