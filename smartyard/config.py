from functools import lru_cache
from typing import Any

from dotenv import dotenv_values

from smartyard.exceptions import VariableNotSetException


class Config:
    def __init__(self, filename: str) -> None:
        self.__dict__.update(dotenv_values(filename))

    def __getattr__(self, attribute: str) -> Any:
        if attribute not in self.__dict__:
            raise VariableNotSetException(attribute)
        return self.__getattribute__(attribute)

    def __str__(self) -> str:
        return "\n".join({f'"{var}" = "{val}"' for var, val in self.__dict__.items()})


@lru_cache
def get_config(filename=".env") -> Config:
    return Config(filename)
