import datetime
import json
import uuid

from typing import Any
from django.conf import settings
from rest_framework.request import Request
import requests
from mpesa.gateway.base import MpesaBase
from mpesa.models import B2BTransaction


class B2B(MpesaBase):
    """
    A class for interacting with the M-Pesa API to perform b2c transactions.
    """
    def __init__(self):
        """
        Initializes the MpesaGateWay with necessary configurations.
        """
        super().__init__()
        self.b2b_url = settings.MPESA_B2B_URL
        self.b2b_callback_url = settings.BASE_URL + settings.MPESA_B2B_CALLBACK_URL
        self.security_credentials = settings.MPESA_SECURITY_CREDENTIALS

    def b2b_send(self, request: Request, amount: int, paybill_num: int, account_num: str, remarks: str, phone_number=None) -> dict:
        """
        Send a B2B payment request.
        Parameters:
        request (Request): The HTTP request object.
        amount (int): The amount to be transferred.
        paybill_num (int): The paybill number of the recipient.
        account_num (str): The account reference for the transaction.
        remarks (str): Additional remarks for the transaction.
        phone_number (str, optional): The phone number of the requester. Defaults to None.
        Returns:
        dict: The response data from the B2B payment request.

        This method constructs a payload with the required details for a B2B payment request and sends it to the B2B URL.
        If the request is successful, it logs the transaction details in the B2BTransaction model.
        """
        originator_conversation_id = str(uuid.uuid4())
        payload = {
            "OriginatorConversationID": originator_conversation_id,
            "Initiator": self.username[0],
            "SecurityCredential": self.security_credentials,
            "Command ID": "BusinessPayBill",
            "SenderIdentifierType": 4,
            "RecieverIdentifierType":4,
            "Amount": amount,
            "PartyA": self.short_code,
            "PartyB": paybill_num,
            "AccountReference": account_num,
            "Requester": phone_number,
            "Remarks": remarks,
            "QueueTimeOutURL": self.b2b_callback_url,
            "ResultURL": self.b2b_callback_url,
        }

        response = requests.request(
            "POST",
            self.b2b_url,
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
            B2BTransaction.objects.create(
                conversation_id=conversation_id,
                ip=ip,
                remarks=remarks,
                transaction_amount=amount,
                paybill_number=paybill_num,
                account_reference=account_num
            )
        return response_data

    def b2b_get_transaction_object(self, data: dict) -> B2BTransaction:
        conversation_id = data["Result"]["ConversationId"]
        transaction, _ = B2BTransaction.objects.get_or_create(
            conversation_id=conversation_id
        )
        return transaction

    def b2b_handle_successful_pay(self, data: dict, transaction: B2BTransaction) -> B2BTransaction:
        """
        Retrieve or create a B2BTransaction object based on the provided data.
        Parameters:
        data (dict): The data containing the conversation ID of the transaction.
        Returns:
        B2BTransaction: The retrieved or newly created B2BTransaction object.
        This method extracts the conversation ID from the provided data and uses it to retrieve
        or create a B2BTransaction object in the database.
        """
        items = data["Result"]["ResultParameters"]["ResultParameter"]
        update_fields = {
            "transaction_id": data["Result"]["TransactionID"]
        }
        for item in items:
            if item["Key"] == "DebitAccountBalance":
                update_fields["debit_account_balance"] = items["Value"]
            elif item["Key"] == "DebitPartyAffectedAccountBalance":
                update_fields["debit_party_affected_account_balance"] = items["Value"]
            elif item["Key"] == "DebitPartyAffectedAccountBalance":
                update_fields["debit_party_affected_account_balance"] = items["Value"]
            elif item["Key"] == "TransCompletedTime":
                date = items["Value"]
                update_fields["transaction_time"] = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M:%S')
            elif item["Key"] == "DebitPartyCharges":
                update_fields["debit_party_charges"] = items["Value"]
            elif item["Key"] == "ReceiverPartyPublicName":
                update_fields["recipient_public_name"] = items["Value"]
            elif item["Key"] == "Currency":
                update_fields["currency"] = items["Value"]
            elif item["Key"] == "InitiatorAccountCurrentBalance":
                update_fields["currency"] = items["Value"]

        transaction.update(**update_fields)  # type: ignore

        return transaction

    def b2b_callback_handler(self, data: dict) -> B2BTransaction:
        """
        Handles the callback for a B2B payment transaction.

        Checks the status of the transaction, retrieves or creates a B2BTransaction object,
        and if the status indicates success, updates the transaction with the relevant details.
        Finally, it saves the transaction object with the updated status.

        Parameters:
        data (dict): The dictionary containing the response data from the B2C transaction callback.

        Returns:
        B2BTransaction: The updated B2CTransaction object.
        """
        status = self.check_status(data)
        transaction = self.b2b_get_transaction_object(data)
        if status == 0:
            self.b2b_handle_successful_pay(data, transaction)

        transaction.status = status
        transaction.save()
        return transaction
