import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

def get_digicash_token():
    username = os.getenv("DIGICASH_API_USER")
    password = os.getenv("DIGICASH_API_PASS")
    if not username or not password:
        raise Exception("DIGICASH_API_USER or DIGICASH_API_PASS not set in the environment.")

    auth_str = f"{username}:{password}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/json",
        "User-Agent": "PnL-AutomationBot/1.0"
    }

    # You can switch between UAT and production by changing this line
    url = "https://api.fastpayph.com/auth"  # <- production endpoint

    payload = {}

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        raise Exception(f"Digicash Auth failed: {resp.status_code} {resp.text}")

    data = resp.json()
    if "data" not in data or "token" not in data["data"]:
        raise Exception("No token in Digicash response.")

    return data["data"]["token"]
