import json
from typing import Any

import requests
from pytest_mock import MockerFixture

from smartyard.proxy import Billing

BILLING_URL = "https://billing.ru/api/"


class PostMock:
    def __init__(self, output: dict) -> None:
        self.args = None
        self.kwargs = None
        self.output = output

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.args = args
        self.kwargs = kwargs
        return self

    def json(self) -> dict:
        return self.output


def test_get_address_list(mocker: MockerFixture):
    phone = 79001234567
    expected = {
        "response": "response",
    }
    mock = PostMock(expected)
    mocker.patch.object(requests, "post", mock)
    billing = Billing(BILLING_URL)

    output = billing.get_address_list(phone)

    assert mock.args == (f"{BILLING_URL}getaddresslist",)
    assert mock.kwargs == {
        "headers": {"Content-Type": "application/json"},
        "data": json.dumps({"phone": phone}),
    }
    assert output == expected


def test_create_invoice(mocker: MockerFixture):
    login, amount, phone = "user", "100", "79001234567"
    expected = {
        "response": "response",
    }
    mock = PostMock(expected)
    mocker.patch.object(requests, "post", mock)
    billing = Billing(BILLING_URL)

    output = billing.create_invoice(login, amount, phone)

    assert mock.args == (f"{BILLING_URL}createinvoice",)
    assert mock.kwargs == {
        "headers": {"Content-Type": "application/json"},
        "data": json.dumps({"login": login, "amount": amount, "phone": phone}),
    }
    assert output == expected


def test_get_list(mocker: MockerFixture):
    phone = 79001234567
    expected = {
        "response": "response",
    }
    mock = PostMock(expected)
    mocker.patch.object(requests, "post", mock)
    billing = Billing(BILLING_URL)

    output = billing.get_list(phone)

    assert mock.args == (f"{BILLING_URL}getlist",)
    assert mock.kwargs == {
        "headers": {"Content-Type": "application/json"},
        "data": json.dumps({"phone": phone}),
    }
    assert output == expected
