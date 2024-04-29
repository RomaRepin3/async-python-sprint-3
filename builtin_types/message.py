from datetime import datetime
from typing import Any
from typing import Dict

from settings import DATETIME_FORMAT


class Message:
    """
    Класс сообщения.
    """

    def __init__(self, sending_time: datetime, sender_name: str, text: str):
        self._sending_time = sending_time
        self._sender = sender_name
        self._text = text

    def __str__(self) -> str:
        return f'[{self._sending_time}] {self._sender}: {self._text}'

    @property
    def sending_time(self) -> datetime:
        return self._sending_time

    def to_dict(self) -> Dict[str, Any]:
        """
        Получение информации о сообщении в формате словаря.

        :return: Словарь с информацией о сообщении.
        """
        return {
            'sending_time': self.sending_time.strftime(DATETIME_FORMAT),
            'sender': self._sender,
            'text': self._text
        }
