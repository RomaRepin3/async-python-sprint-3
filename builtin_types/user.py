from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from settings import DATETIME_FORMAT
from .chat import Chat


class User:
    """
    Класс пользователя.
    """

    def __init__(self, name: str, creation_datetime: Optional[datetime] = None, chats: Optional[List[str]] = None):
        self._name = name
        self._creation_datetime = creation_datetime or datetime.now()
        self._chats = chats or list()

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    async def chats(self) -> List[str]:
        return self._chats

    @property
    def creation_datetime(self) -> datetime:
        return self._creation_datetime

    async def add_chat(self, chat: Chat) -> None:
        """
        Добавляет чат в список.

        :param chat: Объект чата.
        :return: None.
        """
        self._chats.append(chat.name)

    def to_dict(self) -> Dict[str, Any]:
        """
        Получение информации о пользователе в формате словаря.

        :return: Словарь с информацией о пользователе.
        """
        return {
            'name': self.name,
            'creation_datetime': self._creation_datetime.strftime(DATETIME_FORMAT),
            'chats': self._chats
        }
