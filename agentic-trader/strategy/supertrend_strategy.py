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
        close = np.array([x['close'] for x in data])
        high = np.array([x['high'] for x in data])
        low = np.array([x['low'] for x in data])

        atr = talib.ATR(high, low, close, timeperiod=self.atr_period)
        hl2 = (high + low) / 2
        upper_band = hl2 + (self.factor * atr)
        lower_band = hl2 - (self.factor * atr)

        # Basic signal
        if close[-1] > upper_band[-1]:
            self.signal = "BUY"
        elif close[-1] < lower_band[-1]:
            self.signal = "SELL"
        else:
            self.signal = "HOLD"

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
        return ask_llm(f"Explain this signal to a novice trader:\n{context}")
