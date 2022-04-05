"""Модуль проксирования запросов к биллингу"""
import json
import urllib.parse

import requests


class Billing:
    """Проксирование запросов к биллингу

    Параметры:
    - url - базовый адрес биллинга, например, http://localhost:8080/api/
    """

    def __init__(self, url: str) -> None:
        self._url = url

    def get_address_list(self, phone: int) -> dict:
        """Запрос списка доступных адресов по номеру телефона

        Параметры:
        - phone - телефон в виде целого числа
        """
        return self._make_json_request(
            self._generate_url("getaddresslist"), {"phone": phone}
        )

    def create_invoice(self, login: str, amount: str, phone: str) -> dict:
        """Запрос списка доступных адресов по номеру телефона

        Параметры:
        - login - идентификатор пользователя в виде строки
        - amount - сумма в виде строки
        - phone - номер телефона в виде строки
        """
        return self._make_json_request(
            self._generate_url("createinvoice"),
            {"login": login, "amount": amount, "phone": phone},
        )

    def get_list(self, phone: int) -> dict:
        """Запрос списка счетов/платежей адресов по номеру телефона

        Параметры:
        - phone - телефон в виде целого числа
        """
        return self._make_json_request(self._generate_url("getlist"), {"phone": phone})

    def _generate_url(self, uri: str) -> str:
        return urllib.parse.urljoin(self._url, uri)

    def _make_json_request(self, url: str, data: dict) -> dict:
        return requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
        ).json()
