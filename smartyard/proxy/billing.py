import json

import requests


class Billing:
    def __init__(self, url: str) -> None:
        self._url = url

    def get_address_list(self, phone: int) -> dict:
        return requests.post(
            self._url + "getaddresslist",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"phone": phone}),
        ).json()

    def create_invoice(self, login: str, amount: str, phone: str) -> dict:
        return requests.post(
            self._url + "createinvoice",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"login": login, "amount": amount, "phone": phone}),
        ).json()

    def get_list(self, phone: int) -> dict:
        return requests.post(
            self._url + "getlist",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"phone": phone}),
        ).json()
