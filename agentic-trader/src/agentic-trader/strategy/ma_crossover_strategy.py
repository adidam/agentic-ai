import numpy as np
from .base_strategy import BaseStrategy


class MovingAverageCrossoverStrategy(BaseStrategy):
    def __init__(self, capital, short_window=10, long_window=50):
        super().__init__(capital)
        self.short_window = short_window
        self.long_window = long_window
        self.signal = "HOLD"
        self.last_candle = None

    def analyze_market(self, data):
        close_prices = np.array([x["close"] for x in data])

        if len(close_prices) < self.long_window:
            self.signal = "HOLD"
            return

        short_ma = np.convolve(close_prices, np.ones(
            self.short_window)/self.short_window, mode='valid')
        long_ma = np.convolve(close_prices, np.ones(
            self.long_window)/self.long_window, mode='valid')

        # Align lengths
        offset = len(short_ma) - len(long_ma)
        if offset > 0:
            short_ma = short_ma[offset:]

        # Check for crossover
        if short_ma[-2] < long_ma[-2] and short_ma[-1] > long_ma[-1]:
            self.signal = "BUY"
        elif short_ma[-2] > long_ma[-2] and short_ma[-1] < long_ma[-1]:
            self.signal = "SELL"
        else:
            self.signal = "HOLD"

        self.last_candle = data[-1]

    def generate_signal(self):
        return self.signal

    def calculate_position_size(self):
        risk_per_trade = 0.01 * self.capital  # 1% risk
        price = self.last_candle["close"]
        sl = price * 0.98  # 2% stop loss
        risk_per_unit = price - sl
        qty = int(risk_per_trade / risk_per_unit) if risk_per_unit > 0 else 0
        return qty

    def generate_notes(self):
        return f"MA Crossover Signal: {self.signal} at {self.last_candle['close']}, short={self.short_window}, long={self.long_window}"
