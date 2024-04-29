from datetime import datetime
from typing import Any
from typing import Dict

from builtin_types import Chat
from builtin_types import Message
from builtin_types import User
from data_transfer_objects import RequestDto
from settings import ACTUALITY_PERIOD
from settings import DATETIME_FORMAT


class Factories:
    """
    Фабрики.
    """

    @classmethod
    async def get_empty_private_chat(cls, *users) -> Chat:
        """
        Создание пустого чата.

        :param users: Список имен пользователей.
        :return: Пустой приватный чат.
        """
        return Chat(name=' and '.join(users), messages=[], actuality_period=ACTUALITY_PERIOD)

    @classmethod
    def get_empty_common_chat(cls) -> Chat:
        """
        Создание пустого общеге чата.

        :return: Пустой общий чат.
        """
        return Chat(name='Common', messages=[], actuality_period=ACTUALITY_PERIOD)

    @classmethod
    async def get_message_from_request(cls, user_name: str, request_dto: RequestDto) -> Message:
        """
        Создание сообщения из запроса.

        :param user_name: Имя пользователя.
        :param request_dto: Данные запроса от клиента.
        :return: Объект сообщения.
        """
        return Message(sending_time=datetime.now(), sender_name=user_name, text=request_dto.message)

    @classmethod
    def get_message_from_dict(cls, message_dict: Dict[str, Any]) -> Message:
        """
        Создание сообщения из словаря.

        :param message_dict: Словарь с информацией о сообщении.
        :return: Объект сообщения.
        """
        return Message(
            sending_time=datetime.strptime(message_dict['sending_time'], DATETIME_FORMAT),
            sender_name=message_dict['sender'],
            text=message_dict['text']
        )

    @classmethod
    def get_chat_from_dict(cls, chat_dict: Dict[str, Any]) -> Chat:
        """
        Создание чата из словаря.

        :param chat_dict: Словарь с информацией о чате.
        :return: Объект чата.
        """
        messages = [cls.get_message_from_dict(message) for message in chat_dict['messages']]
        return Chat(name=chat_dict['name'], messages=messages, actuality_period=chat_dict['actuality_period'] // 3600)

    @classmethod
    def get_user_from_dict(cls, user_dict: Dict[str, Any]) -> User:
        """
        Создание пользователя из словаря.

        :param user_dict: Словарь с информацией о пользователе.
        :return: Объект пользователя.
        """
        return User(
            name=user_dict['name'],
            creation_datetime=datetime.strptime(user_dict['creation_datetime'], DATETIME_FORMAT),
            chats=user_dict['chats']
        )
