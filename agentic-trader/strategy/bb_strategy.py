import numpy as np
import talib
from .base_strategy import BaseStrategy


class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, capital, period=20, deviation=2):
        super().__init__(capital)
        self.period = period
        self.deviation = deviation
        self.signal = "HOLD"
        self.last_close = None
        self.last_upper = None
        self.last_lower = None

    def analyze_market(self, data):
        close = np.array([x["close"] for x in data])

        if len(close) < self.period:
            return

        upper, middle, lower = talib.BBANDS(
            close,
            timeperiod=self.period,
            nbdevup=self.deviation,
            nbdevdn=self.deviation,
            matype=0
        )

        self.last_close = close[-1]
        self.last_upper = upper[-1]
        self.last_lower = lower[-1]

        if self.last_close < self.last_lower:
            self.signal = "BUY"
        elif self.last_close > self.last_upper:
            self.signal = "SELL"
        else:
            self.signal = "HOLD"

    def generate_signal(self):
        return self.signal

    def calculate_position_size(self):
        price = self.last_close
        sl = price * 0.97 if self.signal == "BUY" else price * 1.03
        risk_per_unit = abs(price - sl)
        qty = int((0.01 * self.capital) /
                  risk_per_unit) if risk_per_unit > 0 else 0
        return qty

    def generate_notes(self):
        return (
            f"Close: {self.last_close:.2f}, "
            f"Upper: {self.last_upper:.2f}, "
            f"Lower: {self.last_lower:.2f}, "
            f"Signal: {self.signal}"
        )
