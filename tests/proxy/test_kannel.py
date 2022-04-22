"""Модуль тестирования запросов к смс-агрегатору"""

from typing import Any

import pytest
import requests
from pytest_mock import MockerFixture
from requests.exceptions import HTTPError

from smartyard.config import Config
from smartyard.proxy import Kannel


class GetMock:
    """Класс для мокирования пуе-запросов"""

    def __init__(self, exception: Exception) -> None:
        self.args = None
        self.kwargs = None
        self.exception = exception

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.args = args
        self.kwargs = kwargs
        if self.exception:
            raise self.exception("")
        return self

    def json(self) -> dict:
        """Предопределнные данные для теста"""
        return self.output


@pytest.mark.parametrize("exception", (None, HTTPError, Exception))
def test_send_code(test_config: Config, exception: Exception, mocker: MockerFixture):
    """Тест отправки смс с кодом"""
    phone = 79001234567
    code = 1234
    mock = GetMock(exception)
    mocker.patch.object(requests, "get", mock)
    kannel = Kannel(test_config)

    kannel.send_code(phone, code)

    assert mock.args == (
        f"http://{test_config.KANNEL_HOST}:{test_config.KANNEL_PORT}/{test_config.KANNEL_PATH}",
    )
    assert mock.kwargs == {
        "params": (
            ("user", test_config.KANNEL_USER),
            ("pass", test_config.KANNEL_PASS),
            ("from", test_config.KANNEL_FROM),
            ("coding", test_config.KANNEL_CODING),
            ("to", phone),
            (
                "text",
                f"{test_config.KANNEL_TEXT}{code}".encode("utf-16-be")
                .decode("utf-8")
                .upper(),
            ),
        ),
    }
