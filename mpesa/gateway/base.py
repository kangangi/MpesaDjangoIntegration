import json
import logging

from django.conf import settings
from django.core.cache import cache

from rest_framework.serializers import ValidationError
import requests
from requests.auth import HTTPBasicAuth

logging = logging.getLogger("default")

class MpesaBase:
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

