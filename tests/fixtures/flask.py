"""Модуль фикстур Flask-приложения"""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from smartyard import config, create_app


@pytest.fixture
def app(test_config: config.Config) -> Flask:
    """Фикстура Flask-приложения"""
    flask_app, _ = create_app(test_config)
    flask_app.config.update({"TESTING": True})
    yield flask_app


@pytest.fixture
# pylint: disable=redefined-outer-name
def flask_client(app) -> FlaskClient:
    """Фикстура клиента для теста Flask-приложения"""
    return app.test_client()
