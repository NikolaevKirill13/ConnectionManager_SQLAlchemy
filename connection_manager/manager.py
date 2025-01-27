from typing import Callable
from contextlib import asynccontextmanager
from functools import wraps


class ConnectionManager:
    """
    Менеджер подключений к базе данных. Создает сессии для одной или нескольких баз данных.
    Работает с помощью декоратора attach_session.
    """
    def __init__(self, **kwargs) -> None:
        """
        :param kwargs: async_sessionmaker
        """
        for name, session_factory in kwargs.items():
            self._create_async_session_method(session_factory, name)

    def _create_async_session_method(self, session_factory, name: str):
        """
        Создает метод для получения асинхронной сессии.
        """

        @asynccontextmanager
        async def get_async_session():
            async with session_factory() as session:
                try:
                    yield session
                except Exception as e:
                    await session.rollback()  # Откат транзакции при ошибке
                    raise e
                finally:
                    await session.close()
        setattr(self, f"get_async_{name}", get_async_session)

    def attach_session(self, *names: str):
        """
        Декоратор для привязки одной или нескольких асинхронных сессий к функции.
        """
        def wrapper(func: Callable):
            @wraps(func)
            async def inner(*args, **kwargs):
                sessions = {}
                for name in names:
                    session_name = f"get_async_{name}"
                    async with getattr(self, session_name)() as session:
                        sessions[name] = session
                kwargs.update(sessions)
                return await func(*args, **kwargs)

            return inner

        return wrapper