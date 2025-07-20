import numpy as np
import talib
from .base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    def __init__(self, capital, rsi_period=14, oversold=30, overbought=70):
        super().__init__(capital)
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.signal = "HOLD"
        self.last_rsi = None
        self.last_candle = None

    def analyze_market(self, data):
        close = np.array([x["close"] for x in data])
        self.last_candle = data[-1]
        if len(close) < self.rsi_period:
            return

        rsi = talib.RSI(close, timeperiod=self.rsi_period)
        self.last_rsi = rsi[-1]

        if self.last_rsi < self.oversold:
            self.signal = "BUY"
        elif self.last_rsi > self.overbought:
            self.signal = "SELL"
        else:
            self.signal = "HOLD"

    def generate_signal(self):
        return self.signal

    def calculate_position_size(self):
        risk = 0.01 * self.capital
        price = self.last_candle["close"]
        sl = price * 0.97 if self.signal == "BUY" else price * 1.03
        risk_per_unit = abs(price - sl)
        qty = int(risk / risk_per_unit) if risk_per_unit > 0 else 0
        return qty

    def generate_notes(self):
        return f"RSI: {self.last_rsi:.2f}, signal: {self.signal} at {self.last_candle['close']}"
