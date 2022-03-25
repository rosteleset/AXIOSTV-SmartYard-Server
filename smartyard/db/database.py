"""Модуль для работы с подключением к базе данных"""
import functools

from flask_sqlalchemy import SQLAlchemy


@functools.lru_cache
def create_db_connection():
    """Создание объекта подключения к базе данных"""
    return SQLAlchemy()
