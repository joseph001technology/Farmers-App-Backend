import requests
import base64
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET")
SHORTCODE = os.environ.get("MPESA_SHORTCODE", "174379")
PASSKEY = os.environ.get("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
CALLBACK_URL = "https://josephkiarie2.pythonanywhere.com/api/payments/mpesa/callback/"

# 🔒 SANDBOX SAFETY GUARD — always use test number during sandbox
SAFE_TEST_NUMBER = "254708374149"
SANDBOX_MODE = True  # ← set to False only when going live


def get_access_token():
    if not CONSUMER_KEY or not CONSUMER_SECRET:
        raise Exception("MPesa credentials not set in .env")

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get("access_token")


def stk_push(phone, amount, account_reference="Order", transaction_desc="Payment"):
    access_token = get_access_token()

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        (SHORTCODE + PASSKEY + timestamp).encode()
    ).decode()

    # Normalize phone to 2547XXXXXXXX
    phone = str(phone).strip()
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]

    # 🔒 SAFETY: force test number in sandbox mode
    if SANDBOX_MODE:
        phone = SAFE_TEST_NUMBER

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()