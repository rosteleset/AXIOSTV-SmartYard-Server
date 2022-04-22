"""Модуль описания таблицы, хранящей коды аутентификации"""
from sqlalchemy import BigInteger, Column, Integer

from smartyard.db.database import Base, BaseModel


class Temps(Base, BaseModel):
    """Таблица с кодами для аутентификации

    Колонки:
    - userphone - номер телефона
    - smscode - код для SMS
    """

    __tablename__ = "temps"

    userphone = Column(BigInteger, primary_key=True)
    smscode = Column(Integer, index=True, unique=True)

    def __init__(self, userphone, smscode):
        self.userphone = userphone
        self.smscode = smscode

    def __eq__(self, _temp: "Temps") -> bool:
        return self.userphone == _temp.userphone and self.smscode == _temp.smscode
