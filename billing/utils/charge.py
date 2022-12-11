import requests
import json
import hashlib
import base64
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad


FLUTTERWAVE_SECRET = "FLWSECK_TEST-9dbffbbda5a3746b8e37eb4456886097-X"
FLUTTERWAVE_PUBLIC = "FLWPUBK_TEST-c103ae5a1628c16c68bc77451af5c1f1-X"
CHARGE_CARD_ENDPOINT = "https://api.flutterwave.com/v3/charges?type=card"
MOBILE_MONEY_ENDPOINT = "https://api.flutterwave.com/v3/charges?type=mobile_money_"
MPESA_ENDPOINT = "https://api.flutterwave.com/v3/charges?type=mpesa"
ENCRYPTION_KEY = "FLWSECK_TEST5b63f3a70b92"
TOKENISED_TRANSACTIONS = "https://api.flutterwave.com/v3/tokenized-charges"


# Function that charges a card using flutterwave api


def charge_card(card_number, cvv, expiry_month, expiry_year, transaction_id, amount, email, currency="USD"):

    payload = {
        "amount": amount,
        "tx_ref": transaction_id,
        "currency": currency,
        "card_number": card_number,
        "cvv": cvv,
        "expiry_month": expiry_month,
        "expiry_year": expiry_year,
        "email": email,
    }

    headers = {
        "Authorization": "Bearer " + FLUTTERWAVE_SECRET,
        "Content-Type": "application/json",
    }

    # Encrypt the payload using  3DES algorithm
    payload = json.dumps(payload)
    payload = payload.encode("utf-8")
    encryption_key = ENCRYPTION_KEY.encode("utf-8")
    cipher = DES3.new(encryption_key, DES3.MODE_ECB)
    payload = cipher.encrypt(pad(payload, DES3.block_size))
    payload = base64.b64encode(payload)
    payload = payload.decode("utf-8")

    # Send the request to the api
    response = requests.post(
        CHARGE_CARD_ENDPOINT, headers=headers, data=json.dumps(
            {"client": payload})
    )

    return response.json()


""" resp = charge_card(
    "5531886652142950",
    "564",
    "09",
    "32",
    "143456789",
    "1000",
    "jimjunior854@gmail.com",
)
print(resp) """


def charge_mobile_money(phone_number, transaction_id, order_id, amount, email, country="uganda", currency="USD", network="MTN"):
    endpoint = MOBILE_MONEY_ENDPOINT + country

    payload = {
        "amount": amount,
        "tx_ref": transaction_id,
        "currency": currency,
        "email": email,
        "phone_number": phone_number,
        "order_id": order_id,
    }

    if country == "ghana":
        payload["network"] = network

    headers = {
        "Authorization": "Bearer " + FLUTTERWAVE_SECRET,
        "Content-Type": "application/json",
    }

    response = requests.request(
        "POST", endpoint, headers=headers, data=json.dumps(payload))
    return response.json()


resp = charge_mobile_money(
    "256704203035",
    "564",
    "03209",
    "32000",
    "jimjunior854@gmail.com",
    "uganda",
)
print(resp)


def charge_mpesa(phone_number, transaction_id, order_id, amount, email, country="kenya"):
    currency = "KES"
    endpoint = MPESA_ENDPOINT + country
    if country == "kenya":
        currency = "KES"
    elif country == "tanzania":
        currency = "TZS"

    payload = {
        "amount": amount,
        "tx_ref": transaction_id,
        "currency": currency,
        "email": email,
        "phone_number": phone_number,
        "order_id": order_id,
    }

    headers = {
        "Authorization": "Bearer " + FLUTTERWAVE_SECRET,
        "Content-Type": "application/json",
    }

    response = requests.request(
        "POST", endpoint, headers=headers, data=json.dumps(payload))
    return response.json()


def verify_transaction(transaction_id):
    endpoint = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {
        "Authorization": "Bearer " + FLUTTERWAVE_SECRET,
        "Content-Type": "application/json",
    }

    response = requests.request("GET", endpoint, headers=headers)
    return response.json()


def charge_card_token(card_token, transaction_id, amount, email, currency="USD"):
    payload = {
        "amount": amount,
        "tx_ref": transaction_id,
        "currency": currency,
        "email": email,
        "token": card_token,
    }

    headers = {
        "Authorization": "Bearer " + FLUTTERWAVE_SECRET,
        "Content-Type": "application/json",
    }

    response = requests.request(
        "POST", TOKENISED_TRANSACTIONS, headers=headers, data=json.dumps(payload))
    return response.json()