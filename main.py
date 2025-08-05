from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime, timedelta
from auth import get_digicash_token
from digicash_api import fetch_transactions
from fees import calc_fees
from sheet_manager import authorize_google_sheets, append_or_update_summary, ensure_columns
import gspread

from pytz import timezone

REQUIRED_HEADERS = [
    "name", "merchant_id", "sheet_url",
    "payin_rate", "qrph_fee", "gcash_fee", "payout_fee",
    "Active"
]

def ensure_headers(sheet):
    existing = sheet.row_values(1)
    if existing != REQUIRED_HEADERS:
        print("🔧 Merchant Config Sheet: Writing headers...")
        sheet.clear()
        sheet.append_row(REQUIRED_HEADERS)
    else:
        print("✅ Merchant Config Sheet: Headers already exist.")

def main():
    client = authorize_google_sheets()
    print("🔐 Using service account:", client.service_account_email)
    today = datetime.now()

    config_sheet_url = os.getenv("MERCHANT_CONFIG_SHEET_URL")
    if not config_sheet_url:
        raise Exception("MERCHANT_CONFIG_SHEET_URL not set.")
    
    config_sheet = client.open_by_url(config_sheet_url).sheet1
    ensure_headers(config_sheet)
    merchants = config_sheet.get_all_records()

    if merchants:
        try:
            debug_url = merchants[0]["sheet_url"]
            print("🔗 Trying test access to:", debug_url)
            debug_sheet = client.open_by_url(debug_url).sheet1
            print("🧪 TEST ACCESS OK:", debug_sheet.title)
        except Exception as e:
            print("❌ TEST ACCESS FAILED:")
            print("🔍 Error details:", e)

    token = get_digicash_token()
    ph_time = timezone("Asia/Manila")

    for m in merchants:
        print("🔍 Merchant:", m.get("name"))
        print("🔗 Sheet URL:", m.get("sheet_url"))

        if not m.get("Active", True):
            continue
        merchant_id = m.get("merchant_id")
        if not merchant_id or not m.get("sheet_url"):
            print(f"⚠️ Skipping {m.get('name','UNKNOWN')} (missing merchant_id or sheet_url)")
            continue

        # Start from an early default date
        start_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
        end_date = today
        first_date_found = False

        # Find first actual transaction date
        while start_date <= end_date:
            start_dt = ph_time.localize(datetime.combine(start_date, datetime.min.time()))
            end_dt = ph_time.localize(datetime.combine(start_date, datetime.max.time()))

            transactions = fetch_transactions(token, merchant_id, start_dt.isoformat(), end_dt.isoformat())
            if transactions:
                print(f"📆 First transaction found: {start_date.strftime('%Y-%m-%d')}")
                first_date_found = True
                break
            start_date += timedelta(days=1)

        if not first_date_found:
            print(f"⚠️ No transactions found for {m['name']}")
            continue

        current_date = start_date
        while current_date <= end_date:
            print(f"📊 Processing {m['name']} for {current_date.strftime('%Y-%m-%d')}")

            start_dt = ph_time.localize(datetime.combine(current_date, datetime.min.time()))
            end_dt = ph_time.localize(datetime.combine(current_date, datetime.max.time()))

            transactions = fetch_transactions(token, merchant_id, start_dt.isoformat(), end_dt.isoformat())
            print(f"🔢 {len(transactions)} transactions fetched.")

            if not isinstance(transactions, list) or not all(isinstance(t, dict) for t in transactions):
                print(f"❌ Invalid transaction format on {current_date.strftime('%Y-%m-%d')}, skipping.")
                current_date += timedelta(days=1)
                continue

            print(f"🧪 Sample transaction: {transactions[0] if transactions else 'No data'}")

            data = calc_fees(transactions, m)
            data["raw_transactions"] = transactions

            try:
                target_sheet = client.open_by_url(m["sheet_url"]).sheet1
                ensure_columns(target_sheet)
            except gspread.exceptions.APIError:
                print(f"❌ Cannot access {m['sheet_url']}. Make sure it's shared to your service account.")
                break

            append_or_update_summary(target_sheet, current_date, data)
            current_date += timedelta(days=1)

        print(f"✅ Finished updating {m['name']}")

    print("🎉 All merchants updated.")

if __name__ == "__main__":
    main()
