import json
import logging
import re
from typing import Any

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
        self.organization_name = settings.ORGANIZATION_NAME

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

    def check_status(self, data: dict) -> Any:
        """
        Checks the status of a payment transaction from the provided data.

        Extracts the status code from the 'Result' field in the data. If there is an exception
        (e.g., the 'Result' field is missing), it logs the error and defaults the status to 1.

        Parameters:
        data (dict): The dictionary containing the response data from the B2C transaction.

        Returns:
        Any: The status code of the transaction. Returns 1 if an error occurs during extraction.
        """
        try:
            status = int(data["Result"]["ResultCode"])
            if status != 0:
                status = 2
        except Exception as e:
            logging.error(e)
            status = 2
        return status

    def get_value(self, data, search_key):
        """
        Extracts a numeric value associated with a search key from a string.
        Uses a regular expression to find and extract the value associated with the specified search key.
        Args:
            data (str): The string data to search within.
            search_key (str): The key to search for.
        Returns:
            str or None: The extracted value as a string, or None if the key is not found.
        """
        # Create a dynamic regex pattern to search for the key and its value
        pattern = "{}=(\d+\.\d+)".format(search_key)

        # Use regular expression to find the value for the given key
        match = re.search(pattern, data)
        if match:
            return match.group(1)
        else:
            return None

