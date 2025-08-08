import requests
from auth import get_digicash_token

DIGICASH_BASE_URL = "https://api.fastpayph.com"

def fetch_transactions(start_time, end_time, txn_type, service_id):
    """
    Fetch transactions from Digicash API (pay or payout) using Bearer token and service ID.
    """
    assert txn_type in {"pay", "payout"}, "txn_type must be 'pay' or 'payout'"

    url = f"{DIGICASH_BASE_URL}/reports/{txn_type}"
    token = get_digicash_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "PnL-AutomationBot/1.0"
    }

    params = {
        "startDate": start_time,
        "endDate": end_time,
        "serviceId": service_id
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        res_json = response.json()

        if res_json.get("code") == 1000 and res_json.get("request", {}).get("status") == "ok":
            return res_json["request"].get("data", [])
        else:
            print(f"⚠️ Unexpected response format or error: {res_json}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {txn_type} transactions for serviceId {service_id}: {e}")
        return []
