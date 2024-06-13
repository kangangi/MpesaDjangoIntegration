import base64
import logging
import datetime

import pytz
from typing import Tuple
from django.conf import settings

from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.request import Request
import requests

from mpesa.gateway.base import MpesaBase
from mpesa.models import STKTransaction

logging = logging.getLogger("default")


class Express(MpesaBase):
    """
    A class for interacting with the M-Pesa API to perform STK Push transactions.
    """
    def __init__(self):
        """
        Initializes the MpesaGateWay with necessary configurations.
        """
        super().__init__()
        self.stk_push_url = settings.MPESA_STK_PUSH_URL
        self.stk_callback_url = settings.BASE_URL + settings.MPESA_STK_CALLBACK_URL
        self.api_key = settings.MPESA_API_KEY

    def generate_password(self) -> Tuple[str, str]:
        """
        Generates the password used for authenticating STK Push requests.
        Returns:
           Tuple[str, str]: The generated password and timestamp.
        """
        timestamp = datetime.datetime.now(pytz.timezone("Africa/Nairobi")).strftime("%Y%m%d%H%M%S")
        password_str = self.short_code + self.api_key + timestamp
        password_bytes = password_str.encode("ascii")
        return base64.b64encode(password_bytes).decode("utf-8"), timestamp

    def stk_push(
            self, request: Request, amount: int, phone_number: str, description: str, reference: str
    ) -> dict:
        """
        Initiates an STK Push transaction.
        Args:
            request: The Django request object.
            amount (int): The transaction amount.
            phone_number (str): The customer's phone number.
            description (str): Description of the transaction.
            reference (str): Reference for the transaction.
        Returns:
            dict: Response data from the M-Pesa API.
        """
        password, timestamp = self.generate_password()
        payload = {
            "BusinessShortCode": self.short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": self.stk_callback_url,
            "AccountReference": reference,
            "TransactionDesc": description,
        }

        response = requests.post(
            self.stk_push_url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.get_access_token()),
            }
        )
        response_data = response.json()

        if response.ok:
            ip = request.META.get("REMOTE_ADDR")
            checkout_request_id = response_data.get("CheckoutRequestID", None)
            STKTransaction.objects.create(
                phone_number=phone_number,
                checkout_request_id=checkout_request_id,
                reference=reference,
                description=description,
                amount=amount,
                ip=ip
            )
        return response_data

    def stk_check_status(self, data: dict) -> int:
        """
        Extracts the status code from the callback data.
        Args:
            data (dict): The callback data received from the M-Pesa API.
        Returns:
            int: The status code extracted from the data. Returns 1 if extraction fails.
        """
        try:
            status = data["Body"]["stkCallback"]["ResultCode"]
        except Exception as e:
            logging.error(e)
            status = 1
        return status

    def stk_get_transaction_object(self, data: dict) -> STKTransaction:
        """
        Retrieves or creates a Transaction object based on the checkout request ID.
        Args:
            data (dict): The callback data received from the M-Pesa API.
        Returns:
            Transaction: The Transaction object corresponding to the checkout request ID.
        """
        checkout_request_id = data["Body"]["stkCallBack"]["CheckoutRequestID"]
        transaction, _ = STKTransaction.objects.get_or_create(
            checkout_request_id=checkout_request_id
        )
        return transaction

    def stk_handle_successful_pay(self, data: dict, transaction: STKTransaction) -> STKTransaction:
        """
        Handles a successful payment by updating the Transaction object with relevant information.
        Args:
            data (dict): The callback data received from the M-Pesa API.
            transaction (Transaction): The Transaction object to be updated.
        Returns:
            Transaction: The updated Transaction object.
        """
        items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
        amount, phone_number, receipt_no, transaction_date = None, None, None, None
        for item in items:
            if item["Name"] == "Amount":
                amount = item["Value"]
            elif item["Name"] == "MpesaReceiptNumber":
                receipt_no = items["Value"]
            elif item["Name"] == "PhoneNumber":
                phone_number = item["Value"]
            elif item["Name"] == "TransactionDate":
                transaction_date = item["Value"]

            transaction.amount = amount
            transaction.phone_number = PhoneNumber(raw_input=phone_number)
            transaction.receipt_no = receipt_no
            transaction.transaction_date = transaction_date

        return transaction

    def stk_callback_handler(self, data):
        """
        Handles the callback data received from the M-Pesa API.
        Args:
          data (dict): The callback data received from the M-Pesa API.
        Returns:
          Transaction: The Transaction object updated based on the callback data.
        """
        status = self.stk_check_status(data)
        transaction = self.stk_get_transaction_object(data)
        if status == 0:
            self.stk_handle_successful_pay(data, transaction)

        transaction.status = status
        transaction.save()

        return transaction
