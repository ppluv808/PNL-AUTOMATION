import requests
from datetime import datetime
from pytz import timezone
import base64
import os

PH_TZ = timezone("Asia/Manila")

USERNAME = os.getenv("DIGICASH_API_USER")
PASSWORD = os.getenv("DIGICASH_API_PASS")
MERCHANT_SERVICE_ID = os.getenv("Ventaja")  # Required

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

def fetch_transactions(start_date, end_date, type_):
    assert type_ in {"pay", "payout"}, "type_ must be either 'pay' or 'payout'"

    if not USERNAME or not PASSWORD or not MERCHANT_SERVICE_ID:
        raise EnvironmentError("Missing DIGICASH_API_USER, DIGICASH_API_PASS, or FASTPAY_MERCHANT_SERVICE_ID in environment variables.")

    url = f"https://api.fastpayph.com/reports/{type_}"
    start_dt = datetime.fromisoformat(start_date).astimezone(PH_TZ)
    end_dt = datetime.fromisoformat(end_date).astimezone(PH_TZ)

    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode(),
        "Accept": "application/json"
    }
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "merchantServiceId": MERCHANT_SERVICE_ID
    }

    print(f"📦 Fetching {type_} transactions from FastPay API")
    print("🔗 URL:", url)
    print("📅 Date Range:", params["startDate"], "to", params["endDate"])

    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and "result" in data and "items" in data["result"]:
                items = data["result"]["items"]
            else:
                items = data.get("data", data)

            if not isinstance(items, list):
                raise ValueError("Expected list of transactions.")

            classified = [classify_transaction(t) for t in items]
            filtered = filter_by_date(classified, start_dt, end_dt)

            print(f"✅ Retrieved {len(filtered)} {type_} transactions")
            return filtered

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed:", e)
            if attempt == 2:
                raise
            import time
            time.sleep(2 ** attempt)
