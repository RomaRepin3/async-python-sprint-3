from argparse import ArgumentParser
from argparse import Namespace
from asyncio import open_connection
from asyncio import run
from json import dumps


class Client:
    """
    Клиент для обмена сообщениями с сервером.
    """

    def __init__(self, client_name: str, server_host: str, server_port: int):
        if not isinstance(client_name, str):
            raise TypeError('client_name must be str')

        self._client_name = client_name
        self._server_host = server_host
        self._server_port = server_port

    async def _send(self, endpoint: str, message: str, recipient: str, chat_name: str) -> str:
        """
        Отправка запроса.

        :param endpoint: Эндпоинт сервера.
        :param message: Сообщение.
        :param recipient: Получатель.
        :param chat_name: Название чата.
        :return: Строковый ответ сервера.
        """
        reader, writer = await open_connection(self._server_host, self._server_port)

        request = dumps(
            {
                'client_name': self._client_name,
                'endpoint': endpoint,
                'message': message,
                'recipient': recipient,
                'chat_name': chat_name,
            }
        )
        writer.write(request.encode())
        writer.write_eof()
        await writer.drain()

        response = await reader.read()
        encoded_response = response.decode()
        writer.close()
        return encoded_response

    async def connect_user(self) -> str:
        """
        Подключение пользователя к серверу.

        :return: Строковый ответ сервера.
        """
        return await self._send(endpoint='connect', message='', recipient='', chat_name='')

    async def get_status(self) -> str:
        """
        Запрос статуса пользователя.

        :return: Строковый ответ сервера.
        """
        return await self._send(endpoint='status', message='', recipient='', chat_name='')

    async def send_message(self, text: str, recipient: str = ''):
        """
        Отправка сообщения.

        :param text: Текст сообщения.
        :param recipient: Получатель, если не указан, то отправляется всем.
        :return: Строковый ответ сервера.
        """
        return await self._send(endpoint='send', message=text, recipient=recipient, chat_name='')

    async def read_chat(self, chat_name: str) -> str:
        """
        Чтение чата.

        :param chat_name: Название чата.
        :return: Строковый ответ сервера.
        """
        return await self._send(endpoint='read_chat', message='', recipient='', chat_name=chat_name)

    async def start_session(self) -> None:
        """
        Запуск сессии клиента.

        :return: None.
        """
        print(await self.connect_user())

        while True:
            print('Выберите действие:\n1. Показать статус\n2. Отправить сообщение\n3. Показать чат\n4. Выход')
            action = input()
            if not action.isdigit():
                continue
            action = int(action)
            if action == 1:
                print(await self.get_status())
            elif action == 2:
                message: str
                while True:
                    message = input('Сообщение: ')
                    if message:
                        break
                recipient = input('Кому: ')
                print(await self.send_message(message, recipient))
            elif action == 3:
                chat_name = input('Название чата: ')
                print(await self.read_chat(chat_name))
            elif action == 4:
                break


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-c', '--client_name', type=str, help='Name of client')
    parser.add_argument('-s', '--server_host', type=str, default='127.0.0.1', help='Host of server')
    parser.add_argument('-p', '--server_port', type=int, default=8000, help='Port of server')
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    client = Client(client_name=args.client_name, server_host=args.server_host, server_port=args.server_port)

    try:
        await client.start_session()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    exit(0)


if __name__ == '__main__':
    run(main())
