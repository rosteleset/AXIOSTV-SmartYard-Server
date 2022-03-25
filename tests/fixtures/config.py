import os

import pytest

from smartyard.config import Config, get_config


@pytest.fixture
def env_file() -> str:
    return os.path.join(os.path.dirname(__file__), "data", "test.env")


@pytest.fixture
def test_config(env_file: str) -> Config:
    return get_config(env_file)
