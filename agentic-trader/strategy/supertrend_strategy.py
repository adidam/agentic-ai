import talib
import numpy as np
from llm_router import ask_llm
from .base_strategy import BaseStrategy


class SupertrendStrategy(BaseStrategy):
    def __init__(self, capital, factor=3.0, atr_period=10):
        super().__init__(capital)
        self.factor = factor
        self.atr_period = atr_period
        self.last_candle = None
        self.signal = "HOLD"

    def analyze_market(self, data):
        # Extract OHLC arrays
        try:
            close = np.array([x['close'] for x in data], dtype=np.float64)
            high = np.array([x['high'] for x in data], dtype=np.float64)
            low = np.array([x['low'] for x in data], dtype=np.float64)
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error processing market data {e}")
            return

        # Check if arrays are empty or too short for ATR calculation
        if len(close) < self.atr_period or len(high) < self.atr_period or len(low) < self.atr_period:
            self.signal = "HOLD"  # Not enough data to calculate ATR
            return

        # Check for NaN or Inf values after creation, as TALIB can be sensitive
        if not (np.all(np.isfinite(close)) and np.all(np.isfinite(high)) and np.all(np.isfinite(low))):
            print(
                "Warning: Input data contains NaN or infinite values. This might affect TALIB calculations.")
            # You might want to handle these non-finite values (e.g., fill with previous valid value, remove, etc.)
            # For now, we'll proceed, but it's good to be aware.
        atr = talib.ATR(high, low, close, timeperiod=self.atr_period)

        if np.isnan(atr[-1]):
            self.signal = "HOLD"
            return

        hl2 = (high + low) / 2

        # Ensure upper_band and lower_band are also calculated using finite ATR values
        if np.isfinite(atr[-1]):
            upper_band = hl2 + (self.factor * atr)
            lower_band = hl2 - (self.factor * atr)
        else:
            # If ATR is not finite, we cannot calculate bands reliably
            self.signal = "HOLD"
            return

        # Basic signal
        # Ensure we have enough elements in the bands and close prices to compare
        if len(close) > 0 and len(upper_band) > 0 and len(lower_band) > 0:
            if close[-1] > upper_band[-1]:
                self.signal = "BUY"
            elif close[-1] < lower_band[-1]:
                self.signal = "SELL"
            else:
                self.signal = "HOLD"
        else:
            self.signal = "HOLD"  # Not enough data for a signal

        if data:  # Only assign last_candle if data is not empty
            self.last_candle = data[-1]

    def generate_signal(self):
        return self.signal

    def calculate_position_size(self):
        risk_per_trade = 0.01 * self.capital  # 1% risk
        price = self.last_candle['close']
        sl = price * 0.98  # 2% stop loss
        risk_per_unit = price - sl
        qty = int(risk_per_trade / risk_per_unit) if risk_per_unit > 0 else 0
        return qty

    def generate_notes(self):
        context = f"Supertrend signal: {self.signal} at {self.last_candle['close']}"
        return ask_llm(f"Explain this signal to a novice trader:\n{context}", "groq")
