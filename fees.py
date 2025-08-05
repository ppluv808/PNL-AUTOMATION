def calc_fees(transactions, merchant):
    gcash_payins = []
    qrph_payins = []
    payouts = []

    for t in transactions:
        t['fee'] = 0  # Default

        if t['type'] == 'payin':
            method = t.get('method', '').lower()
            if method == 'gcash':
                t['fee'] = t['amount'] * 0.025
                gcash_payins.append(t)
            elif method == 'qrph':
                t['fee'] = 7
                qrph_payins.append(t)
        elif t['type'] == 'payout':
            t['fee'] = float(merchant.get('payout_fee', 15))
            payouts.append(t)

    gcash_sum = sum(t['amount'] for t in gcash_payins)
    qrph_sum = sum(t['amount'] for t in qrph_payins)
    payin_sum = gcash_sum + qrph_sum
    payout_sum = sum(t['amount'] for t in payouts)

    gcash_count = len(gcash_payins)
    qrph_count = len(qrph_payins)
    payout_count = len(payouts)

    gcash_fee = sum(t['fee'] for t in gcash_payins)
    qrph_fee = sum(t['fee'] for t in qrph_payins)
    payout_fee = sum(t['fee'] for t in payouts)

    total_fees = gcash_fee + qrph_fee + payout_fee
    buy_rate = total_fees / payin_sum if payin_sum else 0

    return {
        'payin_sum': payin_sum,
        'payout_sum': payout_sum,
        'gcash_count': gcash_count,
        'qrph_count': qrph_count,
        'payout_count': payout_count,
        'gcash_fee': gcash_fee,
        'qrph_fee': qrph_fee,
        'payout_fee': payout_fee,
        'total_fees': total_fees,
        'buy_rate': buy_rate
    }
