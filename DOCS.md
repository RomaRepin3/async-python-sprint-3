# Документация к проектному заданию

## `Сервер`

Запуск сервера осуществляется из консоли командой:

```shell
python3 server.py
```

Логи сервера выводятся в консоль запуска.

По умолчанию сервер запускает на хосте 127.0.0.1 и порту 8000. 
Данные значения можно переопределить указав необязательные флаги при запуске сервиса, например:

```shell
python3 server.py -s 127.0.0.10 -p 7001 
```

Количество последних сообщений общего чата, доступных новому клиенту можно переопределить в настройках,
 изменив значение `SHARED_CHAT_MESSAGES_LIMIT`. Сообщения во всех чатах хранятся 1 час 
(можно переоперделить, изменив настройку `ACTUALITY_PERIOD`), актуализация сообщений производится при добавлении 
сообщений в чат, а также при чтении. Настройки сервера хранятся в файле `settings.py`.

Эндпоинты сервера:

- connect - подключение/регистрация пользователя
- status - получение информации о пользователях и чатах
- send - отправка сообщения
- read_chat - чтение чата

Для завершения работы сервера необходимо нажать сочетание клавиш `Ctrl + C` в сессии терминала, в которой бы запущен 
сервер. При остановке таким способом данные о работе сервера записываются в файл `server_config.json`, откуда будут 
восстановлены при повторном запуске. 

## `Клиент`

Запуск клиента осуществляется в терминале командой:

```shell
python3 client.py -c <Имя клиента>
```

Новые сессии клиентов необходимо создавать в отдельных сессиях терминала.

Запуск клиента без имени невозможен. 
Взаимодействие с сервером осуществляется через диалог в консоли. 
При отправке сообщения без указания адресата сообщение попадает в общий чат.
Для отправки сообщения в персональный чат необходимо указать имя пользователя-получателя.
После каждой отправки сообщения клиенту выводится ответ от сервера в строковом виде.

Для остановки сервра необходимо выбрать соответствующий вариант в диалоге в терминале или нажать сочетание 
клавиш `Ctrl + C`.