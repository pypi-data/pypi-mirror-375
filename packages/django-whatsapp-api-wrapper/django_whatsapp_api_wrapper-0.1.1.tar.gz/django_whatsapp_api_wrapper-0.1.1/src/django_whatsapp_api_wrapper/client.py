import logging
import requests
from django.conf import settings
from .messages import Message


class WhatsApp:
    def __init__(
        self,
        token: str = settings.TOKEN,
        phone_number_id: str = settings.PHONE_NUMBER_ID #Default to the phone number id from the settings,
    ):
        """
        Initialize the WhatsApp Object

        Args:
            token[str]: Token for the WhatsApp cloud API
            phone_number_id[str]: Phone number id for the WhatsApp cloud API
        """

        if token == "":
            logging.error("Token not provided")
            raise ValueError("Token not provided but required")
        if phone_number_id == "":
            logging.error("Phone number ID not provided")
            raise ValueError("Phone number ID not provided but required")

        self.PACKAGE_VERSION = settings.PACKAGE_VERSION  # package version
        self.API_VERSION = settings.API_VERSION  # api version

        self.token = token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/{self.API_VERSION}"
        self.url = f"{self.base_url}/{phone_number_id}/messages"
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def build_message(self, **kwargs) -> Message:
        """
        Build a message object

        Args:
            data[dict]: The message data
            content[str]: The message content
            to[str]: The recipient
            rec_type[str]: The recipient type (individual/group)
        """
        return Message(**kwargs, instance=self)
