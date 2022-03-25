"""Модуль класса-конфигурации сервиса"""
from functools import lru_cache
from typing import Any

from dotenv import dotenv_values

from smartyard.exceptions import VariableNotSetException


class Config:
    """Класс-конфигурации сервиса Умный двор
    Параметры читаются из указанного файла.
    При этом есть ряд переменных со значениями по умолчанию:
        KANNEL_CODING=2
        KANNEL_PATH=cgi-bin/sendsms
        PG_PORT=5432

    Параметры:
    - filename - имя/путь к файлу настроек"""

    def __init__(self, filename: str) -> None:
        values = {
            "KANNEL_CODING": "2",
            "KANNEL_PATH": "cgi-bin/sendsms",
            "PG_PORT": "5432",
        }
        values.update(dotenv_values(filename))
        self.__dict__.update(values)

    def __getattr__(self, attribute: str) -> Any:
        if attribute not in self.__dict__:
            raise VariableNotSetException(attribute)
        return self.__getattribute__(attribute)

    def __str__(self) -> str:
        return "\n".join({f'"{var}" = "{val}"' for var, val in self.__dict__.items()})


@lru_cache
def get_config(filename=".env") -> Config:
    """Создать класс-конфигурации для указанного файла
    Для каждого файла создается только один объект класса.

    Параметры:
    - filename - имя/путь к файлу настроек"""
    return Config(filename)
