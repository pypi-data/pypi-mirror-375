def text(self, text: str, preview_url: bool = False) -> dict:

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": self.rec,
        "to": self.to,
        "type": "text",
        "text": {"preview_url": preview_url, "body": self.content},
    }
    
    return data