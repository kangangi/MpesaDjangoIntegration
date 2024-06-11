import base64
import json
import logging
import datetime
import uuid

import pytz
from typing import Tuple, Any
from django.conf import settings
from django.core.cache import cache

from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.serializers import ValidationError
from rest_framework.request import Request
import requests
from requests.auth import HTTPBasicAuth

from mpesa.models import STKTransaction, B2CTransaction

logging = logging.getLogger("default")


class MpesaGateWay:
    """
    A class for interacting with the M-Pesa API to perform STK Push transactions.
    """
    def __init__(self):
        """
        Initializes the MpesaGateWay with necessary configurations.
        """
        self.short_code = settings.MPESA_SHORT_CODE
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.access_token_url = settings.MPESA_ACCESS_TOKEN_URL
        self.username = settings.MPESA_USERNAME

        self.stk_push_url = settings.MPESA_STK_PUSH_URL
        self.stk_callback_url = settings.BASE_URL + settings.MPESA_STK_CALLBACK_URL
        self.api_key = settings.MPESA_API_KEY

        self.b2c_url = settings.MPESA_B2C_URL
        self.b2c_callback_url = settings.BASE_URL + settings.MPESA_B2C_CALLBACK_URL
        self.security_credentials = settings.MPESA_SECURITY_CREDENTIALS

    def get_access_token(self) -> str:
        """
        Retrieves the access token required for making requests to the M-Pesa API.
        Returns:
            str: The access token.
        """
        token = cache.get("mpesa_access_token")
        if not token:
            try:
                basic_auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)
                response = requests.get(self.access_token_url, auth=basic_auth)
                response_data = json.loads(response.text)
                token, expiry = response_data.get('access_token'),  response_data.get('expires_in')
                cache.set(key="mpesa_access_token", value=token, timeout=float(expiry))
            except Exception as e:
                logging.error("Error {}".format(e))
                raise ValidationError("Invalid credentials")
        return token

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

    def b2c_send(self, request: Request, amount: int, phone_number: str, occassion: str, remarks: str) -> dict:
        """
        Sends a B2C (Business to Customer) payment request to the specified phone number.

        This method constructs the payload with the necessary parameters and sends a POST request to the B2C URL.
        If the request is successful (HTTP 200 status), it extracts the conversation ID from the response and
        logs the transaction in the B2CTransaction model along with the IP address of the requester, occassion, and
        remarks.

        Parameters:
        request (Request): The Django request object containing metadata about the request, such as the IP address.
        amount (int): The amount of money to be sent to the recipient.
        phone_number (str): The recipient's phone number.
        occassion (str): A description of the occasion for the transaction.
        remarks (str): Additional remarks or comments about the transaction.

        Returns:
        dict: A dictionary containing the response data from the B2C payment request.
        """
        originator_conversation_id = str(uuid.uuid4())
        payload = {
            "OriginatorConversationID": originator_conversation_id,
            "InitiatorName": self.username[0],
            "SecurityCredential": self.security_credentials,
            "CommandID": "BusinessPayment",
            "Amount": amount,
            "PartyA": self.short_code,
            "PartyB": phone_number,
            "Remarks": remarks,
            "QueueTimeOutURL": self.b2c_callback_url,
            "ResultURL": self.b2c_callback_url,
            "Occassion": occassion,
        }

        response = requests.request(
            "POST",
            self.b2c_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.get_access_token()),
            },
            data=json.dumps(payload)
        )
        response_data = response.json()

        if response.status_code == 200:
            conversation_id = response_data.get('ConversationID')
            ip = request.META.get("REMOTE_ADDR")
            B2CTransaction.objects.create(
                conversation_id=conversation_id,
                ip=ip,
                occassion=occassion,
                remarks=remarks,
                originator_conversation_id=originator_conversation_id,
                recipient_phonenumber=phone_number,
                transaction_amount=amount
            )
        return response_data

    def b2c_check_status(self, data: dict) -> Any:
        """
        Checks the status of a B2C payment transaction from the provided data.

        Extracts the status code from the 'Result' field in the data. If there is an exception
        (e.g., the 'Result' field is missing), it logs the error and defaults the status to 1.

        Parameters:
        data (dict): The dictionary containing the response data from the B2C transaction.

        Returns:
        Any: The status code of the transaction. Returns 1 if an error occurs during extraction.
        """
        try:
            status = data["Result"]["ResultCode"]
            if status != 0:
                status = 1
        except Exception as e:
            logging.error(e)
            status = 1
        return status

    def b2c_get_transaction_object(self, data: dict) -> B2CTransaction:
        """
        Retrieves or creates a B2CTransaction object based on the conversation ID from the provided data.

        Extracts the conversation ID from the 'Result' field in the data and uses it to get or create
        a B2CTransaction object.

        Parameters:
        data (dict): The dictionary containing the response data from the B2C transaction.

        Returns:
        B2CTransaction: The retrieved or newly created B2CTransaction object.
        """
        conversation_id = data["Result"]["ConversationId"]
        transaction, _ = B2CTransaction.objects.get_or_create(
            conversation_id=conversation_id
        )
        return transaction

    def b2c_handle_successful_pay(self, data: dict, transaction: B2CTransaction) -> B2CTransaction:
        """
        Handles the successful B2C payment transaction by updating the transaction object with relevant details.

        Extracts various parameters from the 'ResultParameters' field in the data, such as the transaction id,
        receiver's public name, and transaction completion time, and updates the B2CTransaction object.

        Parameters:
        data (dict): The dictionary containing the response data from the successful B2C transaction.
        transaction (B2CTransaction): The B2CTransaction object to be updated.

        Returns:
        B2CTransaction: The updated B2CTransaction object.
        """
        items = data["Result"]["ResultParameters"]["ResultParameter"]
        update_fields = {
            "transaction_id": data["Result"]["TransactionID"]
        }
        for item in items:
            if item["Key"] == "ReceiverPartyPublicKey":
                receiver = items["Value"]
                update_fields["recipient_public_Key"] = receiver[1]
            elif item["Key"] == "TransactionCompletedDateTime":
                date = items["Value"]
                update_fields["transaction_time"] = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M:%S')

        transaction.update(**update_fields)  # type: ignore

        return transaction

    def b2c_callback_handler(self, data: dict) -> B2CTransaction:
        """
        Handles the callback for a B2C payment transaction.

        Checks the status of the transaction, retrieves or creates a B2CTransaction object,
        and if the status indicates success, updates the transaction with the relevant details.
        Finally, it saves the transaction object with the updated status.

        Parameters:
        data (dict): The dictionary containing the response data from the B2C transaction callback.

        Returns:
        B2CTransaction: The updated B2CTransaction object.
        """
        status = self.b2c_check_status(data)
        transaction = self.b2c_get_transaction_object(data)
        if status == 0:
            self.b2c_handle_successful_pay(data, transaction)

        transaction.status = status
        transaction.save()

        return transaction
