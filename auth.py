import os
import base64
import requests

def get_digicash_token():
    # ✅ Load from environment
    username = os.getenv("DIGICASH_API_USER")
    password = os.getenv("DIGICASH_API_PASS")

    if not username or not password:
        raise Exception("❌ DIGICASH_API_USER or DIGICASH_API_PASS not set in the environment.")

    # ✅ Basic Auth encoding
    auth_str = f"{username}:{password}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    # ✅ Hardcoded headers (matching Postman)
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/json",
        "User-Agent": "PnL-AutomationBot/1.0"
    }

    url = "https://api.fastpayph.com/auth"  # ✅ Hardcoded production endpoint

    try:
        resp = requests.post(url, headers=headers, json={}, timeout=30)
        resp.raise_for_status()

        data = resp.json()

        if "data" in data and "token" in data["data"]:
            return data["data"]["token"]
        else:
            raise Exception(f"❌ No token in Digicash response: {data}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Digicash Auth request failed: {e}")
