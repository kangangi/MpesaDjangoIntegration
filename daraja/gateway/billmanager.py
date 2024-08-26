import json
import uuid
from typing import List, Dict

from daraja.gateway.base import MpesaBase
from django.conf import settings
from rest_framework.request import Request
import requests
class BillManager(MpesaBase):
    """
    A class for interacting with the M-Pesa API to perform bill manager operations
    """
    def __init__(self):
        """
        Initializes the MpesaGateWay with necessary configurations.
        """
        super().__init__()
        self.bill_manager_onboard_callback_url = settings.MPESA_GENERIC_CALLBACK_URL
        self.bill_manager_onboard_url = settings.MPESA_BILLMANAGER_ONBOARD_URL
        self.bill_manager_single_invoicing_url = settings.MPESA_BILLMANAGER_INVOICING_URL
        self.bill_manager_bulk_invoicing_url = settings.MPESA_BILLMANAGER_BULK_INVOICING_URL

    def onboard(self, email:str, phone_number: str, send_remainders: int, logo=None):
        payload = {
            "shortcode": self.short_code,
            "email": email,
            "officialContact": phone_number,
            "sendReminders": send_remainders,
            "logo": logo if logo else None,
            "callbackurl": self.bill_manager_onboard_callback_url
        }

        response = requests.request(
            "POST",
            self.bill_manager_onboard_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.get_access_token()),
            },
            data=json.dumps(payload)
        )
        response_data = response.json()

        return response_data["resmsg"]

    def single_invoicing_send(
            self, recipient_name: str, recipient_phonenumber: str, billed_period: str, invoice_name:str,
            due_date: str, amount: int, account_reference: str, invoice_items: List[Dict[str:str]]
    ):

        external_reference = str(uuid.uuid4())
        payload = {
            "externalReference": external_reference,
            "billedFullName": recipient_name,
            "billedPhoneNumber": recipient_phonenumber,
            "billedPeriod": billed_period,
            "invoiceName": invoice_name,
            "dueDate": due_date,
            "accountReference": account_reference,
            "amount": amount,
            "invoiceItems": invoice_items
        }
        response = requests.request(
            "POST",
            self.bill_manager_single_invoicing_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.get_access_token()),
            },
            data=json.dumps(payload)
        )
        response_data = response.json()

        return response_data["resmsg"]

    def bulk_invoicing_url(self, invoicing_data: List[Dict]):
        response = requests.request(
            "POST",
            self.bill_manager_bulk_invoicing_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.get_access_token()),
            },
            data=json.dumps(invoicing_data)
        )
        response_data = response.json()

        return response_data["resmsg"]



