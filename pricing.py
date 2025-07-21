def compute_payin_fee(amount, merchant):
    # Tiered pricing for Dypay
    if merchant["name"].lower() == "dypay":
        if amount > 20_000_000:
            rate = 0.02
        elif amount > 15_000_000:
            rate = 0.021
        elif amount > 10_000_000:
            rate = 0.022
        else:
            rate = 0.023
        return amount * rate
    elif merchant["name"].lower() == "ventaja":
        return 0
    return amount * float(merchant.get("payin_rate", 0.015))

def process_transactions(transactions, merchant):
    payins = [t for t in transactions if t["type"] == "payin"]
    payouts = [t for t in transactions if t["type"] == "payout"]
    payin_sum = sum(t["amount"] for t in payins)
    payout_sum = sum(t["amount"] for t in payouts)
    payin_count = len(payins)
    payout_count = len(payouts)
    payin_fee = compute_payin_fee(payin_sum, merchant)
    payout_fee = payout_count * float(merchant.get("payout_fee", 6.5))
    starpay_fee = sum(6 if t["amount"] >= 600 else t["amount"] * 0.01 for t in payins)
    revenue = payin_fee + payout_fee
    buy_rate = round(starpay_fee / payin_sum, 4) if payin_sum else 0
    return {
        "Payins": payin_sum,
        "Payin Count": payin_count,
        "Payouts": payout_sum,
        "Payout Count": payout_count,
        "Revenue": revenue,
        "Starpay Cost": starpay_fee,
        "Buy Rate": buy_rate,
        "Total Fees": payin_fee + payout_fee + starpay_fee
    }