import requests
from mpesa.gateway.base import MpesaBase

from django.conf import settings

class C2B(MpesaBase):
    """
    A class for interacting with the M-Pesa API to perform STK Push transactions.
    """
    def __init__(self):
        """
        Initializes the MpesaGateWay with necessary configurations.
        """
        super().__init__()
        self.c2b_register_url = settings.MPESA_C2B_REGISTER_URL
        self.default_response = settings.MPESA_C2B_DEFAULT_RESPONSE
        self.confirmation_url = settings.MPESA_C2B_CONFIRMATION_URL
        self.validation_url = settings.MPESA_C2B_VALIDATION_URL

    def register_c2b_urls(self):
        payload = {
            "ShortCode": self.short_code,
            "ResponseType": self.default_response,
            "ConfirmationURL": self.confirmation_url,
            "ValidationURL": self.validation_url
        }

        response = requests.request(
            "POST",
            self.c2b_register_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.get_access_token()),
            },
            data=json.dumps(payload)
        )
        response_data = response.json()
        return response_data

    def validation_handler(self, data, validation_parameter):
        pass

    def confirmation_handler(self, data):
        print(data)
