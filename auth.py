import base64
import requests

# 🔐 Replace with your actual production credentials
DIGICASH_API_USER = "your_username_here"
DIGICASH_API_PASS = "your_password_here"

def get_digicash_token():
    if not DIGICASH_API_USER or not DIGICASH_API_PASS:
        raise Exception("DIGICASH_API_USER or DIGICASH_API_PASS not set.")

    auth_str = f"{DIGICASH_API_USER}:{DIGICASH_API_PASS}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/json",
        "User-Agent": "PnL-AutomationBot/1.0"
    }

    url = "https://api.fastpayph.com/auth"  # Production endpoint

    resp = requests.post(url, headers=headers, json={})
    if resp.status_code != 200:
        raise Exception(f"Digicash Auth failed: {resp.status_code} {resp.text}")

    data = resp.json()
    if "data" not in data or "token" not in data["data"]:
        raise Exception("No token found in Digicash response.")

    return data["data"]["token"]
