from kite_connect import fetch_historical
from decision_chain import run_agent
from trail_logger import log_trial_trade
from strategy.ma_crossover_strategy import MovingAverageCrossoverStrategy
from utility import load_top_symbols

# symbol = input("Symbol: ")
starting_capital = 10000
interval = "5minute"  # or "day" for end-of-day strategies

# historical_data = fetch_historical(symbol, interval=interval, duration="day")
# if not historical_data or len(historical_data) < 60:
#     print("Not enough data to warm up strategy.")
#     exit()

# historical_data = fetch_historical(symbol, interval=interval, duration="day")
# if not historical_data or len(historical_data) < 60:
#     print("Not enough data to warm up strategy.")
#     exit()

strategy = MovingAverageCrossoverStrategy(capital=starting_capital)

# strategy.analyze_market(historical_data[-60:])

# signal = strategy.generate_signal()
# current_price = historical_data[-1]["close"]

# print(f"📊 Strategy Signal for {symbol}: {signal} at ₹{current_price}")

# if signal == "BUY":
#     quantity = strategy.calculate_position_size()
#     if quantity > 0:
#         entry_price = current_price
#         total_cost = entry_price * quantity
#         print(
#             f"✅ Simulated BUY: {quantity} units of {symbol} at ₹{entry_price} (₹{total_cost})")
#     else:
#         print("💡 Not enough capital or position size too small.")
# else:
#     print("🚫 No BUY action suggested.")


# Add 5 more candles, simulate next trading day
# strategy.analyze_market(historical_data[-60:] + new_data)

# if strategy.generate_signal() == "SELL":
#     exit_price = new_data[-1]["close"]
#     pnl = (exit_price - entry_price) * quantity
#     print(f"💸 Simulated SELL at ₹{exit_price}, PnL = ₹{pnl}")


def trial_run(symbol, strategy_cls=MovingAverageCrossoverStrategy, capital=10000):
    data = fetch_historical(symbol, interval="day", duration="day")
    if not data or len(data) < 60:
        print("Insufficient data")
        return

    strategy = strategy_cls(capital)
    strategy.analyze_market(data[-60:])
    signal = strategy.generate_signal()
    price = data[-1]["close"]

    print(f"Signal: {signal} at ₹{price}")

    if signal == "BUY":
        qty = strategy.calculate_position_size()
        if qty > 0:
            print(
                f"Simulated BUY: {qty} units at ₹{price} (Total ₹{qty * price})")
        else:
            print("Position size too small or insufficient capital")
    else:
        print("No BUY signal")


def trial_run_with_agent(symbol="INFY", strategy_cls=MovingAverageCrossoverStrategy, capital=10000):
    print(f"fetching symbol {symbol}...")
    data = fetch_historical(symbol, interval="day", duration="day")
    if not data or len(data) < 60:
        print("Insufficient data for strategy warm-up.")
        return

    strategy = strategy_cls(capital)
    strategy.analyze_market(data[-60:])  # warm-up window
    signal = strategy.generate_signal()
    price = data[-1]["close"]
    note = strategy.generate_notes()

    print(f"📈 [{symbol}] Signal: {signal} at ₹{price} — Note: {note}")

    # 🧠 Ask the LLM to explain reasoning
    reasoning = run_agent(data[-60:])  # this function is your LLM call
    print(f"🧠 LLM explanation: {reasoning}")

    # 📝 Log trial decision
    log_trial_trade(symbol, signal, price, strategy_cls.__name__, reasoning)


# trial_run("INFY", MovingAverageCrossoverStrategy)

# symbols = get_top_nse_stocks_by_volume()

symbols = load_top_symbols()

for symbol in symbols:
    print(symbol)
    trial_run_with_agent(symbol.split(":")[-1], MovingAverageCrossoverStrategy)
