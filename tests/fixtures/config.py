"""Модуль фикстур настроек приложения"""

import os

import pytest

from smartyard.config import Config, get_config


@pytest.fixture
def env_file() -> str:
    """Путь к файлу тестовых настроек"""
    return os.path.join(os.path.dirname(__file__), "data", "test.env")


@pytest.fixture
# pylint: disable=redefined-outer-name
def test_config(env_file: str) -> Config:
    """Класс с тестовыми настройками"""
    return get_config(env_file)
