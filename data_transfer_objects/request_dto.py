from dataclasses import dataclass


@dataclass
class RequestDto:
    """
    Данные запроса к серверу.
    """
    client_name: str
    endpoint: str
    message: str
    recipient: str
    chat_name: str
