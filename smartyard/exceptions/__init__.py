"""Пакет классов-ошибок сервиса"""


class VariableNotSetException(Exception):
    """Ошибка: пременная не выставлена

    Параметры:
    - variable_name - имя переменной
    """

    def __init__(self, variable_name: str) -> None:
        super().__init__(f'Variable "{variable_name}" not set')


class NotFoundCodesForPhone(Exception):
    """Ошибка: пользователь по телефону не найден

    Параметры:
    - phone - номер телефона
    """

    def __init__(self, phone: int) -> None:
        super().__init__(f'Codes for phone "{phone}" not found')


class NotFoundCodeAndPhone(Exception):
    """Ошибка: пользователь по номеру телефона и кода не найден

    Параметры:
    - phone - номер телефона
    - code - код из смс
    """

    def __init__(self, phone: int, code: int) -> None:
        super().__init__(f'Code "{code}" for phone "{phone}" not found')
