from contextlib import asynccontextmanager
from functools import wraps
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession


class ConnectionManager:

    """
    Менеджер подключений к базе данных. Создает сессии для одной или нескольких баз данных.
    Работает с помощью декоратора attach_session
    """
    def __init__(self, **kwargs: AsyncSession) -> None:
        """
        :param kwargs: AsyncSession
        """

        # Инициализация соединения или других параметров
        # Создаем сессии для каждого переданного аргумента
        for name, session_factory in kwargs.items():
            self.create_get_session_method(session_factory, name)

    def create_get_session_method(self, session_factory, name):
        """
        Создает метод для получения асинхронной сессии.
        """

        @asynccontextmanager
        async def get_async_session():
            async with session_factory() as session:
                try:
                    yield session
                except Exception as e:
                    await session.rollback()
                    raise e
                finally:
                    await session.close()

        setattr(self, f"get_async_{name}", get_async_session)

    def attach_session(self, *names: str):
        """
        Декоратор для привязки одной или нескольких сессий к функции.
        """
        def wrapper(func: Callable):
            @wraps(func)
            async def inner(*args, **kwargs):
                # Получаем соответствующие асинхронные сессии
                sessions = {}
                for name in names:
                    session_name = f"get_async_{name}"
                    async with getattr(self, session_name)() as session:
                        sessions[name] = session
                        # Объединяем сессии в kwargs
                kwargs.update(sessions)
                return await func(*args, **kwargs)

            return inner

        return wrapper
