from .base_strategy import BaseStrategy
from llm_router import ask_llm


class AIBasedStrategy(BaseStrategy):
    def __init__(self, capital, provider="local", model="llama3-70b-8192"):
        super().__init__(capital)
        self.provider = provider
        self.model = model
        self.signal = "HOLD"
        self.reason = "Awaiting analysis"
        self.last_candle = None

    def analyze_market(self, data):
        self.last_candle = data[-1]
        latest_data = data[-5:]  # last 5 candles
        price_info = "\n".join(
            f"Date: {x['date']}, Open: {x['open']}, High: {x['high']}, Low: {x['low']}, Close: {x['close']}, Volume: {x.get('volume', 'N/A')}"
            for x in latest_data
        )

        prompt = (
            f"Given the following 5-day OHLC market data:\n\n{price_info}\n\n"
            f"As a trading assistant, should I BUY, SELL, or HOLD today? Respond with one word: BUY, SELL, or HOLD, and provide a one-line reason."
        )

        response = ask_llm(prompt, provider=self.provider, model=self.model)

        if "BUY" in response.upper():
            self.signal = "BUY"
        elif "SELL" in response.upper():
            self.signal = "SELL"
        else:
            self.signal = "HOLD"

        self.reason = response

    def generate_signal(self):
        return self.signal

    def calculate_position_size(self):
        price = self.last_candle["close"]
        sl = price * 0.97 if self.signal == "BUY" else price * 1.03
        risk = 0.01 * self.capital
        risk_per_unit = abs(price - sl)
        qty = int(risk / risk_per_unit) if risk_per_unit > 0 else 0
        return qty

    def generate_notes(self):
        return f"AI-based decision: {self.signal}. Reason: {self.reason}"
