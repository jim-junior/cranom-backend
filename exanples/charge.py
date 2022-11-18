import requests

def chargeCard(amount, card_no, cvv, exp_month, exp_year, email):
    url = "https://api.flutterwave.com/v3/charges?type=card"

    payload = {
        "tx_ref": "MC-158940",
        "amount": amount,
        "currency": "NGN",
        "redirect_url": "https://webhook.site/0f1b1b1b-0f1b-1b1b-1b1b-0f1b1b1b1b1b",
        "payment_options": "card",
        "meta": {
            "consumer_id": 23,
            "consumer_mac": "92a3-912ba-1192a"
        },
        "customer": {
            "email": email,
            "phonenumber": "08102909304",
            "name": "yemi desola"
        },
        "card": {
            "card_no": card_no,
            "cvv": cvv,
            "expiry_month": exp_month,
            "expiry_year": exp_year
        }
    }
    