import requests
import json

API_KEY = "TLYZen7EHevzIkM30H1ih8NTRATvs3MShy22KG06SthQV6nKxnWJavk1DsFCfn"
SEND_ENDPOINT = "https://termii.com/api/sms/send"


def send_sms(phonenumber: str, message: str):
    if phonenumber.startswith("+") == True:
        phonenumber = phonenumber[1:]

    payload = {
        "api_key": "TLxsGd7NsUTeIdRuxhKUxuavACR0Tr21ON1Jtrk422YHhvZNjPj0gT5InV42o5",
        "to": phonenumber,
        "from": "SECUREOTP",
        "sms": message,
        "type": "plain",
        "channel": "generic"
    }

    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.request(
        "POST", SEND_ENDPOINT, headers=headers, json=payload)
    return response
