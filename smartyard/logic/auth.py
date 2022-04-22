"""Модуль работы с авторизацией"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Auth:
    """Класс для работы с авторизацией по коду в SMS

    Колонки:
    - userphone - номер телефона
    - smscode - код для SMS
    """

    userphone: int
    smscode: int
