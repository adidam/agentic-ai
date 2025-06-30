import pandas as pd
from datetime import datetime


class BacktestRunner:
    def __init__(self, strategy_cls, capital=100000, **kwargs):
        """
        :param strategy_cls: Strategy class (not instance)
        :param capital: Initial capital
        :param kwargs: Additional arguments to pass to the strategy constructor
        """
        self.strategy_cls = strategy_cls
        self.capital = capital
        self.strategy_kwargs = kwargs
        self.trades = []
        self.pnl = 0

    def run(self, symbol, historical_data):
        strategy = self.strategy_cls(self.capital, **self.strategy_kwargs)
        holding = True
        entry_price = 0
        quantity = 0

        for i in range(60, len(historical_data)):  # Skip first 60 for warmup
            window = historical_data[:i + 1]
            strategy.analyze_market(window)
            signal = strategy.generate_signal()

            candle = window[-1]
            price = candle["close"]

            print(f"signal: {signal}")

            if signal == "BUY" and not holding:
                quantity = strategy.calculate_position_size()
                if quantity > 0:
                    entry_price = price
                    holding = True
                    self.trades.append({
                        "symbol": symbol,
                        "date": candle["date"],
                        "action": "BUY",
                        "price": price,
                        "qty": quantity,
                        "note": strategy.generate_notes()
                    })

            elif signal == "SELL" and holding:
                exit_price = price
                pnl = (exit_price - entry_price) * quantity
                self.pnl += pnl
                holding = False
                self.trades.append({
                    "symbol": symbol,
                    "date": candle["date"],
                    "action": "SELL",
                    "price": exit_price,
                    "qty": quantity,
                    "pnl": pnl,
                    "note": strategy.generate_notes()
                })

            elif signal == "HOLD" and holding:
                # You are holding, and signal is HOLD — just continue holding
                pnl = 0
                self.trades.append({
                    "symbol": symbol,
                    "date": candle["date"],
                    "action": "HOLD",
                    "price": price,
                    "qty": quantity,
                    "pnl": pnl,
                    "note": strategy.generate_notes()
                })

        print(f"trades: {self.trades}")
        return self._generate_report()

    import pandas as pd

    def _generate_report(self):
        if not self.trades:
            return {
                "total_trades": 0,
                "total_pnl": 0.0,
                "win_rate_percent": 0.0,
                "trades": []
            }

        df = pd.DataFrame(self.trades)
        print(df.head())  # Fixed ()

        # Filter by action
        buy_trades = df[df['action'] == 'BUY']
        sell_trades = df[df['action'] == 'SELL']
        hold_trades = df[df['action'] == 'HOLD']

        # Ensure 'pnl' is present and numeric
        sell_trades = sell_trades.copy()
        sell_trades['pnl'] = pd.to_numeric(
            sell_trades.get('pnl', 0), errors='coerce').fillna(0)

        wins = sell_trades[sell_trades['pnl'] > 0].shape[0]
        losses = sell_trades[sell_trades['pnl'] <= 0].shape[0]
        win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0

        total_pnl = sell_trades['pnl'].sum()
        avg_pnl = sell_trades['pnl'].mean() if not sell_trades.empty else 0
        max_win = sell_trades['pnl'].max()
        max_loss = sell_trades['pnl'].min()

        report = {
            "total_trades": len(sell_trades),
            "total_pnl": round(total_pnl, 2),
            "average_pnl_per_trade": round(avg_pnl, 2),
            "max_profit": round(max_win, 2),
            "max_loss": round(max_loss, 2),
            "win_rate_percent": round(win_rate, 2),
            "buy_count": len(buy_trades),
            "sell_count": len(sell_trades),
            "hold_count": len(hold_trades),
            "trades": self.trades  # full trade log
        }

        return report
