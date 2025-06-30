from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    def __init__(self, capital: float):
        self.capital = capital

    @abstractmethod
    def analyze_market(self, ohlc_data):
        pass

    @abstractmethod
    def generate_signal(self):
        pass

    @abstractmethod
    def calculate_position_size(self):
        pass

    @abstractmethod
    def generate_notes(self):
        pass

    def run(self, ohlc_data):
        self.analyze_market(ohlc_data)
        signal = self.generate_signal()
        size = self.calculate_position_size()
        note = self.generate_notes()
        return {
            "signal": signal,
            "size": size,
            "note": note
        }
