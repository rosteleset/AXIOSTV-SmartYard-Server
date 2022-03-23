import os

import pytest

from smartyard.config import Config, get_config
from smartyard.exceptions import VariableNotSetException


@pytest.fixture
def env_file() -> str:
    return os.path.join(os.path.dirname(__file__), "data", "test.env")


def test_one_config_object_for_file(env_file: str) -> None:
    config_first = get_config(env_file)
    config_second = get_config(env_file)
    assert config_first == config_second


def test_exists_variable(env_file: str) -> None:
    config = Config(env_file)
    assert config.PG_HOST == "localhost"


def test_not_exists_variable(env_file: str) -> None:
    config = Config(env_file)
    with pytest.raises(VariableNotSetException):
        config.PG_PORTS
