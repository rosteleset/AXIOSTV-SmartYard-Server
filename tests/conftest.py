"""Модуль настройки фикстур для pytest"""
# pylint: disable=unused-import
import tests.fixtures

pytest_plugins = [
    "tests.fixtures.config",
    "tests.fixtures.database",
    "tests.fixtures.flask",
    "tests.fixtures.logic",
]
