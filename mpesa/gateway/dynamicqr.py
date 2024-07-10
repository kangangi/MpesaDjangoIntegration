from django.conf import settings
import json
import requests
from mpesa.gateway.base import MpesaBase


class DynamicQR(MpesaBase):
    """
    A class for interacting with the M-Pesa API to generate dynamic qr
    """
    def __init__(self):
        """
        Initializes the MpesaGateWay with necessary configurations.
        """
        super().__init__()
        self.dynamic_qr_url = settings.MPESA_DYNAMIC_QR_URL

    def generate_qr(self, transaction_type, amount, reference, party_identifier, merchant_name):
        payload = {
             "MerchantName": merchant_name,
             "RefNo": reference,
             "Amount": amount,
             "TrxCode": transaction_type,
             "CPI": party_identifier,
             "Size": 300
        }

        response = requests.request(
            "POST",
            self.dynamic_qr_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.get_access_token()),
            },
            data=json.dumps(payload)
        )
        response_data = response.json()

        return response_data
