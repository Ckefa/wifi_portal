#!/usr/bin/env python3

import os
import time
import k2connect

from log.logger import getLogger

log = getLogger(__name__)


# Load environment variables
client_id = os.getenv("CLIENT_ID", "").strip()
client_secret = os.getenv("CLIENT_SECRET", "").strip()
base_url = os.getenv("KOPOKOPO_API", "").strip()

if not all((client_id, client_secret, base_url)):
    log.info(f"Env client_id: {client_id}, client_secret{client_secret}, base_url{base_url}")
    log.exception("Missing environment Variable")
    raise Exception("Missing environment Variable")
else:
    log.debug(f"Env variable success client_id: {client_id}, client_secret{client_secret}, base_url{base_url}")


class KopoKopo:
    access_token = None
    expires_in = None

    def __init__(self, uid):
        self.uid = uid
        self.callback_url = None
        if not self.access_token or self.is_token_expired():
            self.get_tokens()

    @classmethod
    def get_tokens(cls):
        """
        Get and refresh the access token if expired.
        """
        # If the access token exists and is still valid, skip fetching a new one
        if cls.access_token and not cls.is_token_expired():
            log.info("Access token is valid, skipping refresh.")
            return

        try:
            # Initialize the library
            k2connect.initialize(client_id, client_secret, base_url)

            # Request a new access token
            authenticator = k2connect.Tokens
            access_token = authenticator.request_access_token()

            # Set class variables for token and expiration
            cls.access_token = access_token.get("access_token")
            cls.expires_in = (
                access_token.get("expires_in") + time.time()
            )  # Expiration time in seconds
            log.info(
                f"New access token acquired: {cls.access_token}, expires in {cls.expires_in - time.time()} seconds."
            )

        except Exception as e:
            log.error(f"Error acquiring access token: {e}")
            raise

    @classmethod
    def is_token_expired(cls):
        """
        Check if the access token is expired.
        """
        if cls.access_token is None:
            return True
        return time.time() >= cls.expires_in

    @classmethod
    def request_payment_status(cls, mpesa_payment_location):
        # Get payment request status
        payment_request_status = k2connect.ReceivePayments.payment_request_status(
            cls.access_token, mpesa_payment_location
        )

        log.debug(f"Mpesa Payment Status: {payment_request_status}")
        return payment_request_status

    def stk_push(self, amount, phone, fname, lname):
        """
        Initiate an STK push payment request.
        """
        # Ensure phone number format (strip leading zero if exists)
        phone = phone[1:] if phone.startswith("0") else phone
        phone = f"+254{phone}"
        log.debug(f"Stk Push to: {phone}")

        try:
            # Create an instance of the Receive Payments service
            receive_payments_service = k2connect.ReceivePayments

            # Prepare the payment request payload
            request_payload = {
                "access_token": self.access_token,
                "callback_url": self.callback_url,
                "first_name": fname,
                "last_name": lname,
                "email": "gadnadolo19@gmail.com",
                "payment_channel": "MPESA",
                "phone_number": phone,
                "till_number": "K118261",
                "amount": amount,
                "metadata": {"hey": "there", "mister": "angelo"},
            }

            # Make the payment request
            mpesa_payment_location = receive_payments_service.create_payment_request(
                request_payload
            )

            return mpesa_payment_location

        except Exception as e:
            log.error(f"Error during STK push: {e}")
            raise

    def request_payment(self, amount, phone, fname, lname, device_id):
        """
        Request a payment by initiating an STK push and setting the callback URL.
        """
        self.callback_url = f"https://ckefa.com:8000/confirm?phone={phone}&amount={amount}&device_id={device_id}"

        try:
            # Make the payment request
            new_order = self.stk_push(amount, phone, fname, lname)
            log.info(f"New payment order created: {new_order}")
            return new_order

        except Exception as e:
            log.error(f"Error during payment request: {e}")
            raise
