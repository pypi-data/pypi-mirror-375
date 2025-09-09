import logging
import requests

class Message:
    # type: ignore
    def __init__(
        self,
        messaging_product: str = "whatsapp",
        to: str = "",
        type: str = "",
        data: dict = {},
        instance: "WhatsApp" = None,
        recipient_type: str = "individual",
    ):
        if instance is not None:
            from .. import WhatsApp
            assert isinstance(instance, WhatsApp)
        self.instance = instance
        self.type = type
        self.data = data
        self.messaging_product = messaging_product
        self.recipient_type = recipient_type
        self.to = to

    def send(self) -> dict:
        try:
            sender = self.instance.phone_number_id
        except:
            logging.error("Phone number id not found")
            
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": self.recipient_type,
            "to": self.to,
        }
            
        if self.type == "text":
            payload.update({
                "type": "text",
                "text": self.data,
            })
        elif self.type == "template":
            payload.update({
                "type": "template",
                "template": self.data,
            })
            
        print(payload)

        logging.info(f"Sending message to {self.to}")
        r = requests.post(self.instance.url, headers=self.instance.headers, json=payload)
        if r.status_code == 200:
            logging.info(f"Message sent to {self.to}")
            return r.json()
        logging.info(f"Message not sent to {self.to}")
        logging.info(f"Status code: {r.status_code}")
        logging.error(f"Response: {r.json()}")
        return r.json()
    
    
