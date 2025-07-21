import requests
import time
import os
import json

def classify_transaction(t):
    method = t.get("method", "").lower()
    bank_name = t.get("bank_name", "").lower()
    account_number = t.get("account_number")
    operation_id = t.get("operation_id", "")

    # Heuristics to determine type
    if method in {"gcash", "grabpay", "palawanpay", "maya"}:
        t["type"] = "payin"
    elif bank_name or account_number:
        t["type"] = "payout"
    elif operation_id.startswith("W"):  # Example: withdrawals often start with "W"
        t["type"] = "payout"
    else:
        t["type"] = "payin"  # Default fallback
    return t

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

            # Support old and new formats
            if isinstance(data, dict) and "result" in data and "items" in data["result"]:
                data = data["result"]["items"]

            if isinstance(data, str):
                data = json.loads(data)

            if not isinstance(data, list):
                raise ValueError("Expected list of transactions, got something else.")

            # Classify each transaction
            return [classify_transaction(t) for t in data]

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
