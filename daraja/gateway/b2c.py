import json
import logging
import datetime
import re
import uuid

from typing import Any
from django.conf import settings
from rest_framework.request import Request
import requests
from daraja.gateway.base import MpesaBase
from daraja.models import B2CTransaction, B2CTopup

logging = logging.getLogger("default")


class B2C(MpesaBase):
    """
    A class for interacting with the M-Pesa API to perform b2c transactions.
    """
    def __init__(self):
        """
        Initializes the MpesaGateWay with necessary configurations.
        """
        super().__init__()
        self.b2c_url = settings.MPESA_B2C_URL
        self.b2c_callback_url = settings.BASE_URL + settings.MPESA_B2C_CALLBACK_URL
        self.security_credentials = settings.MPESA_SECURITY_CREDENTIALS
        self.b2c_topup_url = settings.MPESA_B2C_TOPUP_URL
        self.b2c_topup_callback_url = settings.BASE_URL + settings.MPESA_B2C_TOPUP_CALLBACK_URL

    def b2c_send(self, request: Request, amount: int, phone_number: str, occasion: str, remarks: str) -> dict:
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
        occasion (str): A description of the occasion for the transaction.
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
            "Occassion": occasion,
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
                ip_address=ip,
                occasion=occasion,
                remarks=remarks,
                originator_conversation_id=originator_conversation_id,
                recipient_phonenumber=phone_number,
                transaction_amount=amount
            )
        return response_data

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
        conversation_id = data["Result"]["ConversationID"]
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
        transaction.transaction_id = data["Result"]["TransactionID"]

        for item in items:
            if item["Key"] == "ReceiverPartyPublicName":
                receiver = item["Value"].split("-")
                transaction.recipient_public_name = receiver[1].strip()
            elif item["Key"] == "TransactionCompletedDateTime":
                date = item["Value"]
                transaction.transaction_time = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M:%S')
            elif item["Key"] == "B2CRecipientIsRegisteredCustomer":
                data = item["Value"]
                transaction.is_recipient_registered_customer = True if data == "Y" else False
            elif item["Key"] == "B2CChargesPaidAccountAvailableFunds":
                transaction.charges_paid_available_balance = item["Value"]
            elif item["Key"] == "B2CUtilityAccountAvailableFunds":
                transaction.utility_account_balance = item["Value"]
            elif item["Key"] == "B2CWorkingAccountAvailableFunds":
                transaction.working_account_balance = item["Value"]

        transaction.save()
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
        status = self.check_status(data)
        transaction = self.b2c_get_transaction_object(data)
        if status == 0:
            self.b2c_handle_successful_pay(data, transaction)

        transaction.status = status
        transaction.save()

        return transaction

    def b2c_top_up(
            self, amount: int, paybill_number: int, remarks: str, requester_phone_number="", account_reference="",
            request=None
    ) -> dict:
        """
        Initiates a B2C (Business to Customer) top-up transaction.
        Sends a request to the B2C API to transfer a specified amount to a paybill number.
        The function also logs the transaction details in the B2CTopup model if the request is successful.

        Args:
            amount (int): The amount to be transferred.
            paybill_number (int): The paybill number to which the amount is to be transferred.
            remarks (str): Remarks for the transaction.
            requester_phone_number (str, optional): The phone number of the requester. Defaults to "".
            account_reference (str, optional): Reference for the account. Defaults to "".
            request (HttpRequest, optional): The HTTP request object to extract the remote IP address. Defaults to None.

        Returns:
            dict: Response data from the B2C API.
        """

        payload = {
           "Initiator": self.username[0],
           "SecurityCredential": self.security_credentials,
           "CommandID": "BusinessPayToBulk",
           "SenderIdentifierType": "4",
           "RecieverIdentifierType": "4",
           "Amount": amount,
           "PartyA": self.short_code,
           "PartyB": paybill_number,
           "AccountReference": account_reference,
           "Requester": requester_phone_number,
           "Remarks": remarks,
           "QueueTimeOutURL": self.b2c_topup_callback_url,
           "ResultURL": self.b2c_topup_callback_url
        }

        response = requests.request(
            "POST",
            self.b2c_topup_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.get_access_token()),
            },
            data=json.dumps(payload)
        )
        response_data = response.json()

        if response.status_code == 200:
            conversation_id = response_data.get('ConversationID')
            ip_address = request.META.get("REMOTE_ADDR") if request else ""
            B2CTopup.objects.create(
                conversation_id=conversation_id,
                account_reference=account_reference,
                remarks=remarks,
                ip_address=ip_address,
                requester=requester_phone_number,
                amount=amount,
                paybill_number=paybill_number,

            )
        return response_data

    def b2c_get_transaction_topup_object(self, data: dict) -> B2CTopup:
        """
        Retrieves or creates a B2CTopup transaction object.
        Fetches the B2CTopup transaction from the database using the conversation_id from the provided data.
        If the transaction does not exist, it is created.
        Args:
            data (dict): The data containing the transaction details.
        Returns:
            B2CTopup: The B2CTopup transaction object.
        """
        conversation_id = data["Result"]["ConversationID"]
        transaction, _ = B2CTopup.objects.get_or_create(
            conversation_id=conversation_id
        )
        return transaction

    def b2c_handle_successful_topup(self, data: dict, transaction: B2CTopup) -> B2CTopup:
        """
        Handles a successful B2C top-up transaction.
        Extracts and updates the transaction details from the provided data and saves them in the B2CTopup object.
         Args:
           data (dict): The data containing the transaction details.
           transaction (B2CTopup): The B2CTopup transaction object to update.
        Returns:
           B2CTopup: The updated B2CTopup transaction object.
        """
        items = data["Result"]["ResultParameters"]["ResultParameter"]
        transaction.transaction_id = data["Result"]["TransactionID"]

        for item in items:
            if item["Key"] == "DebitAccountBalance":
                data = item["Value"]
                transaction.debit_account_balance = self.get_value(data, "BasicAmount")
            elif item["Key"] == "TransCompletedTime":
                date = item["Value"]
                transaction.transaction_time = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
            elif item["Key"] == "InitiatorAccountCurrentBalance":
                data = item["Value"]
                transaction.initiator_account_current_balance = self.get_value(data, "BasicAmount")
            elif item["Key"] == "Currency":
                transaction.currency = item["Value"]
            elif item["Key"] == "ReceiverPartyPublicName":
                transaction.receiver_public_name = item["Value"]
            elif item["Key"] == "DebitPartyCharges":
                data = item["Value"]
                transaction.debit_party_charges = data if data else None

        transaction.save()

        return transaction

    def b2c_topup_callback_handler(self, data):
        """
        Handles the B2C top-up callback.
        Processes the callback data to update the transaction status and details.
        Depending on the status, it calls the appropriate handler for the transaction.
        Args:
            data (dict): The callback data containing the transaction details.
        Returns:
            B2CTopup: The updated B2CTopup transaction object.
        """
        status = self.check_status(data)
        transaction = self.b2c_get_transaction_topup_object(data)
        if status == 0:
            self.b2c_handle_successful_topup(data, transaction)
        transaction.status = status
        transaction.save()

        return transaction
