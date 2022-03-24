class VariableNotSetException(Exception):
    def __init__(self, variable_name: str) -> None:
        super().__init__(f'Variable "{variable_name}" not set')


class NotFoundCodesForPhone(Exception):
    def __init__(self, phone: int) -> None:
        super().__init__(f'Codes for phone "{phone}" not found')


class NotFoundCodeAndPhone(Exception):
    def __init__(self, phone: int, code: int) -> None:
        super().__init__(f'Code "{code}" for phone "{phone}" not found')
