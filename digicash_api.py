import requests
import os
from datetime import datetime

DIGICASH_BASE_URL = "https://api.fastpayph.com"

def fetch_transactions(start_time, end_time, txn_type, merchant_id):
    """
    Fetch transactions from Digicash API (pay or payout) for a specific merchant.
    """
    endpoint = f"/reports/{txn_type}"  # txn_type should be "pay" or "payout"
    url = f"{DIGICASH_BASE_URL}{endpoint}"

    params = {
        "startDate": start_time,
        "endDate": end_time,
        "merchant": merchant_id
    }

    username = os.environ.get("DIGICASH_API_USER")
    password = os.environ.get("DIGICASH_API_PASS")

    if not username or not password:
        print("❌ Missing DIGICASH_API_USER or DIGICASH_API_PASS in environment.")
        return []

    try:
        response = requests.get(url, auth=(username, password), params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {txn_type} transactions: {e}")
        return []
