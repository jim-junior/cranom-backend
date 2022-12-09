import requests
import json

FLUTTERWAVE_SECRET = "FLUTTERWAVE_SECRET"
FLUTTERWAVE_PUBLIC = "FLUTTERWAVE_PUBLIC"
CHARGE_CARD_ENDPOINT = "https://api.flutterwave.com/v3/charges?type=card"
MOBILE_MONEY_ENDPOINT = "https://api.flutterwave.com/v3/charges?type=mobile_money_"
MPESA_ENDPOINT = "https://api.flutterwave.com/v3/charges?type=mpesa"

# Function that charges a card using flutterwave api


def charge_card(card_number, cvv, expiry_month, expiry_year, transaction_id, amount, email, currency="UGX"):

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

    response = requests.request(
        "POST", CHARGE_CARD_ENDPOINT, headers=headers, data=json.dumps(payload))
    return response.json()


def charge_mobile_money(phone_number, transaction_id, order_id, amount, email, country="uganda", network="MTN"):
    currency = "UGX"
    endpoint = MOBILE_MONEY_ENDPOINT + country
    if country == "uganda":
        currency = "UGX"
    elif country == "ghana":
        currency = "GHS"
    elif country == "rwanda":
        currency = "RWF"
    elif country == "zambia":
        currency = "ZMW"

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
