from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime, timedelta
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
    ph_time = timezone("Asia/Manila")

    config_sheet_url = os.getenv("MERCHANT_CONFIG_SHEET_URL")
    if not config_sheet_url:
        raise Exception("MERCHANT_CONFIG_SHEET_URL not set.")

    config_sheet = client.open_by_url(config_sheet_url).sheet1
    ensure_headers(config_sheet)
    merchants = config_sheet.get_all_records()

    if merchants:
        try:
            debug_url = merchants[0]["sheet_url"]
            print("🔗 Testing access to:", debug_url)
            debug_sheet = client.open_by_url(debug_url).sheet1
            print("🧪 TEST ACCESS OK:", debug_sheet.title)
        except Exception as e:
            print("❌ TEST ACCESS FAILED:", e)

    for m in merchants:
        name = m.get("name", "UNKNOWN")
        sheet_url = m.get("sheet_url")
        merchant_id = m.get("merchant_id", "").strip()

        is_active = str(m.get("Active", "TRUE")).strip().lower() in {"true", "1", "yes"}

        if not is_active:
            print(f"⏭️ Skipping {name} (inactive)")
            continue
        if not merchant_id or not sheet_url:
            print(f"⚠️ Skipping {name} (missing merchant_id or sheet_url)")
            continue

        start_date = datetime.strptime("2024-01-01", "%Y-%m-%d").date()
        end_date = today.date()

        current_date = start_date
        while current_date <= end_date:
            print(f"\n📊 Processing {name} for {current_date.strftime('%Y-%m-%d')}")

            # PH timezone window: 00:00:00 to 23:59:59
            start_dt = ph_time.localize(datetime.combine(current_date, datetime.min.time()))
            end_dt = ph_time.localize(datetime.combine(current_date, datetime.max.time()))

            try:
                payin_txns = fetch_transactions(start_dt.isoformat(), end_dt.isoformat(), type_="pay", merchant_id=merchant_id)
                payout_txns = fetch_transactions(start_dt.isoformat(), end_dt.isoformat(), type_="payout", merchant_id=merchant_id)
                transactions = payin_txns + payout_txns
            except Exception as e:
                print(f"❌ Fetch failed for {name} on {current_date}: {e}")
                current_date += timedelta(days=1)
                continue

            if not isinstance(transactions, list) or not all(isinstance(t, dict) for t in transactions):
                print(f"❌ Invalid transaction format for {name} on {current_date}, skipping.")
                current_date += timedelta(days=1)
                continue

            print(f"🔢 Transactions fetched: {len(transactions)}")

            data = calc_fees(transactions, m)
            print(f"💰 Payin: {data.get('total_payin', 0)}")
            print(f"💸 Payout: {data.get('total_payout', 0)}")
            print(f"#️⃣ Payout Count: {data.get('payout_tx_count', 0)}")

            data["raw_transactions"] = transactions

            try:
                target_sheet = client.open_by_url(sheet_url).sheet1
                ensure_columns(target_sheet)
                append_or_update_summary(target_sheet, current_date, data)
            except gspread.exceptions.APIError:
                print(f"❌ Cannot access {sheet_url}. Make sure it's shared to your service account.")
                break

            current_date += timedelta(days=1)

        print(f"✅ Finished updating {name}")

    print("🎉 All merchants updated.")

if __name__ == "__main__":
    main()
