import requests
import os
from datetime import datetime, timedelta


DIGICASH_BASE_URL = "https://api.fastpayph.com"

def fetch_transactions(start_time, end_time, txn_type, merchant_id):
    """
    Fetch transactions from Digicash API (pay or payout) for a specific merchant.
    """
    url = f"{DIGICASH_BASE_URL}/reports/{txn_type}"
    params = {
        "startDate": start_time,
        "endDate": end_time,
        "merchant": merchant_id
    }

    auth = (os.environ.get("DIGICASH_API_USER"), os.environ.get("DIGICASH_API_PASS"))

    try:
        response = requests.get(url, auth=auth, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {txn_type} data: {e}")
        return []
