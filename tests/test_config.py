"""Модуль тестирования класса конфигурации"""

import pytest

from smartyard.config import Config, get_config
from smartyard.exceptions import VariableNotSetException


def test_one_config_object_for_file(env_file: str) -> None:
    """Тест проверки одного объекта класса конфигурации на каждый файл"""
    config_first = get_config(env_file)
    config_second = get_config(env_file)
    assert config_first == config_second


def test_exists_variable(env_file: str) -> None:
    """Тест проверки объекта класса конфигурации"""
    config = Config(env_file)
    assert config.PG_HOST == "localhost"


# pylint: disable=pointless-statement
def test_not_exists_variable(env_file: str) -> None:
    """Тест проверки отсутствующего значения в объекте класса конфигурации"""
    config = Config(env_file)
    with pytest.raises(VariableNotSetException):
        config.PG_PORTS
