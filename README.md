# PnL Automation Bot (Digicash Integration)

Automates daily PnL for multiple merchants using Digicash (Fastpay) and Google Sheets.

## Features

- Authenticates with Digicash API (Basic Auth, Fastpay)
- Pulls payin/payout transactions per merchant
- Calculates fees (GCash, QRPH, Payouts, Buy Rate)
- Updates each merchant's PnL Google Sheet daily
- Automatically creates missing columns

## Setup

1. **Clone repo and install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2. **Google Sheets:**
    - Create a Google Cloud project, enable Google Sheets API.
    - Download `service_account.json` to your repo root.

3. **Environment Variables:**
    - `DIGICASH_API_USER` / `DIGICASH_API_PASS` (from Digicash/Fastpay)
    - `MERCHANT_CONFIG_SHEET_URL` (your master merchant config sheet URL)

4. **Merchant Config Sheet:**
    - Should have columns: `name`, `merchant_id`, `payout_fee`, `sheet_url`, `Active`

5. **Run:**

    ```bash
    python main.py
    ```

---

## Notes

- Each merchant must have their own PnL Google Sheet (set in `sheet_url`).
- The config sheet is separate and acts as the master list.

---