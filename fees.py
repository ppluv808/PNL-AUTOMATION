def calc_fees(transactions, merchant):
    gcash_payins = [t for t in transactions if t['type'] == 'payin' and t.get('method', '').lower() == 'gcash']
    qrph_payins = [t for t in transactions if t['type'] == 'payin' and t.get('method', '').lower() == 'qrph']
    payouts = [t for t in transactions if t['type'] == 'payout']
    
    gcash_sum = sum(t['amount'] for t in gcash_payins)
    qrph_sum = sum(t['amount'] for t in qrph_payins)
    payin_sum = gcash_sum + qrph_sum
    payout_sum = sum(t['amount'] for t in payouts)
    
    gcash_count = len(gcash_payins)
    qrph_count = len(qrph_payins)
    payout_count = len(payouts)
    
    gcash_fee = gcash_sum * 0.025
    qrph_fee = qrph_count * 7
    payout_fee = payout_count * float(merchant.get('payout_fee', 15))
    
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