import requests
import time
import os
import json
from datetime import datetime
from pytz import timezone

PH_TZ = timezone("Asia/Manila")

def classify_transaction(t):
    method = t.get("method", "").lower()
    bank_name = t.get("bank_name", "").lower()
    account_number = t.get("account_number")
    operation_id = t.get("operation_id", "")

    if method in {"gcash", "grabpay", "palawanpay", "maya", "qrph"}:
        t["type"] = "payin"
    elif bank_name or account_number:
        t["type"] = "payout"
    elif operation_id.startswith("W"):
        t["type"] = "payout"
    else:
        t["type"] = "payin"
    return t

def filter_by_date(transactions, start_dt, end_dt):
    filtered = []
    for t in transactions:
        timestamp_str = t.get("created_at") or t.get("timestamp")
        if not timestamp_str:
            continue
        try:
            ts = datetime.fromisoformat(timestamp_str)
            if ts.tzinfo is None:
                ts = PH_TZ.localize(ts)
            else:
                ts = ts.astimezone(PH_TZ)
            if start_dt <= ts <= end_dt:
                filtered.append(t)
        except Exception as e:
            print("❌ Error parsing timestamp:", timestamp_str, e)
    return filtered

def fetch_transactions(token, merchant_id, start_date, end_date):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "PnL-AutomationBot/1.0"
    }

    base_url = os.getenv("DIGICASH_API_BASE", "https://uat-api.fastpayph.com")
    url = f"{base_url}/reports/pay"
    payload = {
        "startDate": start_date,
        "endDate": end_date
    }

    print("📦 Requesting FastPay:", url)
    print("📅 Payload:", payload)

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            response_json = resp.json()
            data = response_json.get("data", {})

            if isinstance(data, dict) and "result" in data and "items" in data["result"]:
                data = data["result"]["items"]

            if isinstance(data, str):
                data = json.loads(data)

            if not isinstance(data, list):
                raise ValueError("Expected list of transactions, got something else.")

            transactions = [classify_transaction(t) for t in data]

            # Manual filter by datetime
            start_dt = datetime.fromisoformat(start_date).astimezone(PH_TZ)
            end_dt = datetime.fromisoformat(end_date).astimezone(PH_TZ)
            filtered = filter_by_date(transactions, start_dt, end_dt)

            print(f"✅ {len(filtered)} filtered transactions returned for range.")
            return filtered

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

