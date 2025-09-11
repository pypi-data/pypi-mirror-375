import requests

ENDPOINT = "https://api.pushover.net/1/messages.json"

class Pushover:

    def __init__(self, user_key: str, api_token: str):
        self.user_key = user_key
        self.api_token = api_token

    def send(self, message: str, title: str | None = None, priority: int = 0, sound: str | None = None) -> dict:
        payload = {
            "token": self.api_token,
            "user": self.user_key,
            "message": message,
            "priority": priority
        }
        if title:
            payload["title"] = title
        if sound:
            payload["sound"] = sound

        response = requests.post(ENDPOINT, data=payload)
        return response.json()
