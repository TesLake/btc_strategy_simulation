def print_results(
    bank,
    initial_bank,
    profits_history,
    biggest_trade_percent,
    positive_trades,
    negative_trades,
):
    if bank > initial_bank:
        percent_change = ((bank - initial_bank) / initial_bank) * 100
    else:
        percent_change = (((initial_bank - bank) / initial_bank) * 100) * -1
    print(f"INITIAL BANK ${initial_bank}")
    print(f"FINAL BANK ${bank}")
    print(f"\nPROFIT: ${bank - initial_bank} | {percent_change}% change")
    print(f"BIGGEST TRADE ({biggest_trade_percent})")
    print(f"AVERAGE PROFIT PER TRADE = {sum(profits_history) / len(profits_history)}")
    profits_history.sort()
    print(f"MEDIAN TRADE PROFIT = {profits_history[len(profits_history) // 2]}")
    print(f"POSITIVE TRADES : {positive_trades}")
    print(f"NEGATIVE TRADES : {negative_trades}")
