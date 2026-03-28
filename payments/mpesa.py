import requests
import base64
from datetime import datetime

# 🔥 YOUR CREDENTIALS (sandbox)
CONSUMER_KEY = "YOUR_KEY"
CONSUMER_SECRET = "YOUR_SECRET"
SHORTCODE = "174379"
PASSKEY = "YOUR_PASSKEY"

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get("access_token")


def stk_push(phone, amount, account_reference="Order", transaction_desc="Payment"):
    access_token = get_access_token()

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode()

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": "https://your-domain.com/api/payments/callback/",  # 🔥 change later
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.post(url, json=payload, headers=headers)

    return response.json()