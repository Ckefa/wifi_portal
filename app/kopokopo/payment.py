from dotenv import load_dotenv
import os


import requests
import json


load_dotenv()
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")

base_url = "https://pay.pesapal.com/v3"
print(f"Consumer key {consumer_key}\n", f"consoumer secret {consumer_secret}")


def get_access_token():
    url = f"{base_url}/api/Auth/RequestToken"

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = json.dumps({
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
    })

    response = requests.post(url, headers=headers, data=payload)

    return response.json().get("token")


class Pesapal:
    def __init__(self, order_id):
        self.order_id = order_id
        self.access_token = get_access_token()
        self.callback_url = None
        self.redirect = None
        print("Acess token: ", self.access_token)

    def register_ipn(self):
        url = f"{base_url}/api/URLSetup/RegisterIPN"

        payload = json.dumps({
            "url": self.callback_url,
            "ipn_notification_type": "POST",
        })
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        ipn_id = response.json().get("ipn_id")
        return ipn_id

    def submit_order(self, ipn_id, amount, phone, fname, lname):
        url = f"{base_url}/api/Transactions/SubmitOrderRequest"
        payload = json.dumps({
            "id": self.order_id,
            "currency": "KES",
            "amount": amount,
            "description": "Payment for account upgrade",
            "callback_url": self.callback_url,
            "notification_id": ipn_id,
            "billing_address": {
                "email_address": "",
                "phone_number": phone,
                "country_code": "",
                "first_name": fname,
                "middle_name": "",
                "last_name": lname,
                "line_1": "",
                "line_2": "",
                "city": "",
                "state": "",
                "postal_code": None,
                "zip_code": None,
            },
        })

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        return response

    def payment_status(self, order_track_id):
        url = f"{base_url}/api/Transactions/GetTransactionStatus"

        payload = {}
        params = {"orderTrackingId": order_track_id}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.request(
            "GET", url, headers=headers, params=params, data=payload
        )

        return response.json()

    def request_payment(self, amount, phone, fname, lname):
        self.callback_url = (
            f"https://ckefa.com:8000/confirm?phone={phone}&amount={amount}"
        )
        ipn_id = self.register_ipn()
        new_order = self.submit_order(ipn_id, amount, phone, fname, lname)
        print(new_order)
        self.redirect = new_order["redirect_url"]
        return new_order
