from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from settings import SHARED_CHAT_MESSAGES_LIMIT
from .list_async_iterator import ListAsyncIterator
from .message import Message


class Chat:
    """
    Класс чата.
    """

    def __init__(self, name: str, messages: List[Message], actuality_period: int):
        self._name = name
        self._messages = messages
        self._actuality_period = timedelta(hours=actuality_period)

    @property
    def name(self) -> str:
        return self._name

    async def get_messages(self, user_registration_datetime: Optional[datetime] = None) -> List[Message]:
        """
        Возвращает список сообщений.

        :param user_registration_datetime: Время регистрации пользователя.
        :return: Список сообщений чата.
        """
        if not user_registration_datetime:
            return self._messages
        else:
            messages_indexes_iterator = ListAsyncIterator(list(range(len(self._messages))))
            before_registration_message_index = 0
            async for i in messages_indexes_iterator:
                if self._messages[i].sending_time < user_registration_datetime:
                    before_registration_message_index += 1
                else:
                    break
            if before_registration_message_index > SHARED_CHAT_MESSAGES_LIMIT - 1:
                return self._messages[before_registration_message_index - SHARED_CHAT_MESSAGES_LIMIT:]
            else:
                return self._messages

    async def add_message(self, message: Message, user_registration_datetime: Optional[datetime] = None) -> List[
        Message]:
        """
        Добавление сообщения в чат.

        :param message: Объект сообщения.
        :param user_registration_datetime: Время регистрации пользователя.
        :return: Список сообщений.
        """
        self._messages.append(message)
        return await self.get_messages(user_registration_datetime)

    async def actualize(self) -> None:
        """
        Актуализация списка сообщений.

        :return: None.
        """
        messages_iterator = ListAsyncIterator(self._messages)
        self._messages = [
            msg async for msg in messages_iterator if msg.sending_time > datetime.now() - self._actuality_period
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Получение информации о чате в формате словаря.

        :return: Словарь с информацией о чате.
        """
        return {
            'name': self.name,
            'messages': [message.to_dict() for message in self._messages],
            'actuality_period': self._actuality_period.total_seconds()
        }
