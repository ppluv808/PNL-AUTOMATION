import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

REQUIRED_COLUMNS = [
    "Date", "Payins", "Payouts", "GCash Payin Txn", "QRPH Payin Txn", "Payout Txn",
    "GCash Fees", "QRPH Fees", "Payout Fees", "Total Fees", "Buy Rate", "Settlement", "Ending Balance"
]
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

REQUIRED_COLUMNS = [
    "Date", "Payins", "Payouts", "GCash Payin Txn", "QRPH Payin Txn", "Payout Txn",
    "GCash Fees", "QRPH Fees", "Payout Fees", "Total Fees", "Buy Rate", "Settlement", "Ending Balance"
]

def authorize_google_sheets():
    with open("service_account.json", "r") as f:
        creds_json = json.load(f)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(credentials)
    client.service_account_email = creds_json.get("client_email")
    return client

def ensure_columns(sheet):
    current_headers = sheet.row_values(1)
    if current_headers != REQUIRED_COLUMNS:
        print(f"🛠 Fixing header row to match required columns.")
        sheet.clear()
        sheet.update("A1", [REQUIRED_COLUMNS])
    else:
        print("✅ Merchant sheet headers already correct.")

def append_or_update_summary(sheet, today, data):
    paid_txns = [t for t in data["raw_transactions"] if t.get("status") == "paid"]

    payins = [t for t in paid_txns if t.get("type") == "payin"]
    payouts = [t for t in paid_txns if t.get("type") == "payout"]

    payin_sum = sum(t.get("amount", 0) for t in payins)
    payout_sum = sum(t.get("amount", 0) for t in payouts)

    gcash_txn = [t for t in payins if t.get("method") == "gcash"]
    qrph_txn = [t for t in payins if t.get("method") == "qrph"]
    payout_txn = payouts

    gcash_count = len(gcash_txn)
    qrph_count = len(qrph_txn)
    payout_count = len(payout_txn)

    gcash_fee = sum(t.get("fee", 0) for t in gcash_txn)
    qrph_fee = sum(t.get("fee", 0) for t in qrph_txn)
    payout_fee = sum(t.get("fee", 0) for t in payout_txn)

    total_fees = gcash_fee + qrph_fee + payout_fee
    buy_rate = round(total_fees / payin_sum, 6) if payin_sum else 0

    sheet_data = sheet.get_all_records()
    date_str = today.strftime("%m/%d/%Y")
    row_idx = None

    for idx, row in enumerate(sheet_data, start=2):
        if row.get("Date") == date_str:
            row_idx = idx
            break

    if row_idx is None:
        sheet.append_row([date_str] + [""] * (len(REQUIRED_COLUMNS) - 1))
        row_idx = len(sheet.get_all_values())

    values = [
        payin_sum, payout_sum, gcash_count, qrph_count, payout_count,
        gcash_fee, qrph_fee, payout_fee, total_fees, buy_rate
    ]
    sheet.update(f"B{row_idx}", [values])

    # Settlement and Ending Balance
    settlement_val = sheet.cell(row_idx, 12).value
    try:
        settlement = float(settlement_val)
    except Exception:
        settlement = 0.0

    ending_balance = payin_sum - total_fees - payout_sum - settlement
    sheet.update_cell(row_idx, 13, ending_balance)
