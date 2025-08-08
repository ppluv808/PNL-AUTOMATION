import requests
import os
from datetime import datetime
from auth import get_digicash_token

DIGICASH_BASE_URL = "https://api.fastpayph.com"

def fetch_transactions(start_time, end_time, txn_type, service_id):
    """
    Fetch transactions from Digicash API (pay or payout) using Bearer token and service ID.
    """
    endpoint = f"/reports/{txn_type}"  # txn_type should be "pay" or "payout"
    url = f"{DIGICASH_BASE_URL}{endpoint}"

    token = get_digicash_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "PnL-AutomationBot/1.0"
    }

    params = {
        "startDate": start_time,
        "endDate": end_time,
        "serviceId": service_id  # <-- changed from "merchant" to "serviceId"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {txn_type} transactions: {e}")
        return []
