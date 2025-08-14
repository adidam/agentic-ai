def risk_based_position_size(capital, stop_loss_pct, entry_price):
    risk_amount = capital * 0.01  # 1% risk
    stop_loss = entry_price * (1 - stop_loss_pct)
    loss_per_unit = entry_price - stop_loss
    qty = int(risk_amount / loss_per_unit)
    return qty, stop_loss
