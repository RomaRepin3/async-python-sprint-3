from argparse import ArgumentParser
from argparse import Namespace
from asyncio import StreamReader
from asyncio import StreamWriter
from asyncio import run
from asyncio import start_server
from json import dumps
from json import loads
from logging import INFO
from logging import StreamHandler
from logging import getLogger
from signal import SIGINT
from signal import signal
from sys import stdout
from types import FrameType
from typing import Dict

from builtin_types import Chat
from builtin_types import ListAsyncIterator
from builtin_types import User
from data_transfer_objects import RequestDto
from utils import Factories
from utils import RequestDtoRowMapper

server_logger = getLogger(__name__)
server_logger.setLevel(INFO)
server_logger.addHandler(StreamHandler(stream=stdout))


class Server:
    """
    Сервер для обмена сообщениями с другими клиентами.
    """

    def __init__(self, host: str, port: int, common_chat: Chat, private_chats: Dict[str, Chat], users: Dict[str, User]):
        server_logger.info(f'Create server on {host}:{port}')

        self._host = host
        self._port = port

        self._common_chat = common_chat
        self._private_chats = private_chats
        self._users = users

    def update_from_config(self) -> None:
        """
        Обновление сервера из конфигурационного файла.

        :return: None.
        """
        server_logger.info('Update server from config')

        try:
            with open('server_config.json', 'r') as file:
                server_dict = loads(file.read())
            self._host = server_dict['host']
            self._port = server_dict['port']
            self._common_chat = Factories.get_chat_from_dict(server_dict['common_chat'])
            self._private_chats = {
                private_chat['name']: Factories.get_chat_from_dict(
                    private_chat
                ) for private_chat in server_dict['private_chats']
            }
            self._users = {
                user['name']: Factories.get_user_from_dict(user) for user in server_dict['users']
            }
        except FileNotFoundError:
            server_logger.error('Config file not found')

    def save_to_config(self) -> None:
        """
        Сохранение сервера в конфигурационный файл.

        :return: None.
        """
        server_logger.info('Save server to config')
        server_dict = {
            'host': self._host,
            'port': self._port,
            'common_chat': self._common_chat.to_dict(),
            'private_chats': [private_chat.to_dict() for private_chat in self._private_chats.values()],
            'users': [user.to_dict() for user in self._users.values()],
        }
        with open('server_config.json', 'w') as file:
            file.write(dumps(server_dict, indent=4))

    async def _connect(self, request_dto: RequestDto) -> str:
        """
        Подключение пользователя к серверу.

        :param request_dto: Объект запроса.
        :return: Строковый ответ.
        """
        server_logger.info(f'Client {request_dto.client_name} connected')
        if request_dto.client_name in self._users.keys():
            return 'User already exists'
        self._users[request_dto.client_name] = User(name=request_dto.client_name, chats=[self._common_chat.name])
        return 'OK'

    async def _get_status(self, request_dto: RequestDto) -> str:
        """
        Запрос статуса пользователя.

        :param request_dto: Объект запроса.
        :return: Строковый ответ.
        """
        server_logger.info(f'Client {request_dto.client_name} requested status')
        if request_dto.client_name in self._users.keys():
            chats = await self._users[request_dto.client_name].chats
            users_iterator = ListAsyncIterator(list(self._users.values()))
            other_users = [user.name async for user in users_iterator if user.name != request_dto.client_name]
            return 'Chats:\n' + '\n'.join(chats) + '\n\nUsers:\n' + '\n'.join(other_users)
        return 'User not found'

    async def _send(self, request_dto: RequestDto) -> str:
        """
        Отправка сообщения.

        :param request_dto: Объект запроса.
        :return: Строковый ответ.
        """
        server_logger.info(f'Client {request_dto.client_name} sent message to {request_dto.recipient}')

        if not request_dto.recipient:
            messages = await self._common_chat.add_message(
                message=await Factories.get_message_from_request(request_dto.client_name, request_dto),
                user_registration_datetime=self._users[request_dto.client_name].creation_datetime
            )
            messages_iterator = ListAsyncIterator(list(messages))
            await self._common_chat.actualize()
            return '\n'.join([str(msg) async for msg in messages_iterator])
        else:
            if request_dto.recipient in self._users.keys():
                chat_name: str
                if f'{request_dto.client_name} and {request_dto.recipient}' in self._private_chats.keys():
                    chat_name = f'{request_dto.client_name} and {request_dto.recipient}'
                elif f'{request_dto.recipient} and {request_dto.client_name}' in self._private_chats.keys():
                    chat_name = f'{request_dto.recipient} and {request_dto.client_name}'
                else:
                    new_chat = await Factories.get_empty_private_chat(request_dto.client_name, request_dto.recipient)
                    self._private_chats[new_chat.name] = new_chat
                    chat_name = new_chat.name
                    await self._users[request_dto.client_name].add_chat(chat=new_chat)
                    await self._users[request_dto.recipient].add_chat(chat=new_chat)
                messages = await self._private_chats[chat_name].add_message(
                    message=await Factories.get_message_from_request(request_dto.client_name, request_dto)
                )
                messages_iterator = ListAsyncIterator(list(messages))
                await self._private_chats[chat_name].actualize()
                return '\n'.join([str(msg) async for msg in messages_iterator])
            else:
                return 'Recipient not found'

    async def _read_chat(self, request_dto: RequestDto) -> str:
        """
        Чтение чата.

        :param request_dto: Объект запроса.
        :return: Строковый ответ.
        """
        server_logger.info(f'Client {request_dto.client_name} requested chat {request_dto.client_name}')

        if request_dto.chat_name in self._private_chats.keys():
            await self._private_chats[request_dto.chat_name].actualize()
            messages = await self._private_chats[request_dto.chat_name].get_messages()
            messages_iterator = ListAsyncIterator(list(messages))
            return '\n'.join([str(msg) async for msg in messages_iterator])
        elif request_dto.chat_name == 'Common':
            await self._common_chat.actualize()
            messages = await self._common_chat.get_messages(
                user_registration_datetime=self._users[request_dto.client_name].creation_datetime
            )
            messages_iterator = ListAsyncIterator(list(messages))
            return '\n'.join([str(msg) async for msg in messages_iterator])
        else:
            return 'Chat not found'

    async def _route_request(self, request_dto: RequestDto) -> str:
        """
        Маршрутизация запроса.

        :param request_dto: Данные запроса.
        :return: Ответ от сервера.
        """
        server_logger.info(f'Client {request_dto.client_name} requested {request_dto.endpoint}')
        if request_dto.endpoint == 'connect':
            return await self._connect(request_dto)
        elif request_dto.client_name in self._users.keys():
            if request_dto.endpoint == 'status':
                return await self._get_status(request_dto)
            elif request_dto.endpoint == 'send':
                return await self._send(request_dto)
            elif request_dto.endpoint == 'read_chat':
                return await self._read_chat(request_dto)
        return 'Unknown endpoint or unregister user'

    async def _process_request(self, reader: StreamReader, writer: StreamWriter) -> None:
        """
        Обработчик входящих соединений.

        :return: None.
        """
        address = writer.get_extra_info('peername')
        server_logger.info(f'Start serving {address}')

        request = await reader.read()
        decoded_request = loads(request.decode())
        request_dto = await RequestDtoRowMapper.get_from_dict(decoded_request)
        server_logger.info(f'Received {request_dto} from {address}')

        result = await self._route_request(request_dto)

        writer.write(result.encode())
        server_logger.info(f'Sent {result} to {address}')
        await writer.drain()

        server_logger.info(f'Stop serving {address}')
        writer.close()

    async def listen(self):
        """
        Запуск сервера.

        :return: None.
        """
        server_logger.info(f'Start server on {self._host}:{self._port}')

        server = await start_server(client_connected_cb=self._process_request, host=self._host, port=self._port)

        async with server:
            await server.serve_forever()


def parse_args() -> Namespace:
    """
    Парсинг аргументов командной строки.

    :return: Аргументы командной строки.
    """
    server_logger.info('Parse args')
    parser = ArgumentParser()
    parser.add_argument('-s', '--server_host', type=str, default='127.0.0.1', help='Host of server')
    parser.add_argument('-p', '--server_port', type=int, default=8000, help='Port of server')
    return parser.parse_args()


async def main() -> None:
    """
    Главная функция.

    :return: None.
    """
    args = parse_args()
    server = Server(
        host=args.server_host,
        port=args.server_port,
        common_chat=Factories.get_empty_common_chat(),
        private_chats=dict(),
        users=dict()
    )

    def keyboard_interrupt_handler(signal_number: int, stack_frame: FrameType) -> None:
        """
        Обработчик прерывания клавиатуры.

        :return: None.
        """
        server.save_to_config()
        exit(0)

    signal(SIGINT, keyboard_interrupt_handler)

    try:
        server.update_from_config()
        await server.listen()
    except KeyboardInterrupt:
        server.save_to_config()
        exit(0)


if __name__ == "__main__":
    run(main())
