from functools import lru_cache
from typing import Any

from dotenv import dotenv_values

from smartyard.exceptions import VariableNotSetException


class Config:
    def __init__(self, filename: str) -> None:
        values = {
            "KANNEL_CODING": "2",
            "KANNEL_PATH": "cgi-bin/sendsms",
            "PG_PORT": "5432",
        }
        values.update(dotenv_values(filename))
        self.__dict__.update(values)
        # "BILLING_URL", "KANNEL_HOST", "KANNEL_PORT", "KANNEL_USER", "KANNEL_PASS", "KANNEL_FROM", "KANNEL_TEXT"
        # "PG_USER", "PG_PASS", "PG_HOST", "PG_DBNAME"

    def __getattr__(self, attribute: str) -> Any:
        if attribute not in self.__dict__:
            raise VariableNotSetException(attribute)
        return self.__getattribute__(attribute)

    def __str__(self) -> str:
        return "\n".join({f'"{var}" = "{val}"' for var, val in self.__dict__.items()})


@lru_cache
def get_config(filename=".env") -> Config:
    return Config(filename)
