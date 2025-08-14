import json
from datetime import datetime


def log_trial_trade(symbol, signal, price, strategy_name, note, file_path="logs/trial_trades.jsonl"):
    trade = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "action": signal,
        "price": price,
        "strategy": strategy_name,
        "note": note
    }
    with open(file_path, "a") as f:
        f.write(json.dumps(trade) + "\n")
    print(f"📝 Trial logged: {signal} {symbol} at ₹{price}")
