import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from smartyard import config, create_app


@pytest.fixture
def app(test_config: config.Config) -> Flask:
    app, _ = create_app(test_config)
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def flask_client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app) -> FlaskCliRunner:
    return app.test_cli_runner()
