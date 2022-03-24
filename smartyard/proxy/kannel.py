import requests
from requests.exceptions import HTTPError

from smartyard.config import Config


class Kannel:
    def __init__(self, config: Config) -> None:
        self._config = config

    def send_code(self, phone: int, code: int):
        try:
            sms_text = f"{self._config.KANNEL_TEXT}{code}"
            response = requests.get(
                url=f"http://{self._config.KANNEL_HOST}:{self._config.KANNEL_PORT}/{self._config.KANNEL_PATH}",
                params=(
                    ("user", self._config.KANNEL_USER),
                    ("pass", self._config.KANNEL_PASS),
                    ("from", self._config.KANNEL_FROM),
                    ("coding", self._config.KANNEL_CODING),
                    ("to", phone),
                    ("text", sms_text.encode("utf-16-be").decode("utf-8").upper()),
                ),
            )
            response.raise_for_status()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        else:
            print(f"Success send sms to {phone} and text {sms_text}!")
