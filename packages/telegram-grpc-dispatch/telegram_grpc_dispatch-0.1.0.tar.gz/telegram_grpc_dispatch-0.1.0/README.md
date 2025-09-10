# telegram-notifier

`telegramg-notifier` is a Python library and gRPC-based service for sending messages to **Telegram** in the
background.  
It provides a client–server architecture where clients send messages to the server, and the server delivers them
asynchronously to a specified Telegram chat.

---

## Features

- 📩 **Asynchronous messaging** — messages are sent in the background without blocking the client.
- 🛠 **Multiple client types**:
    - **Simple client** — send messages without extra configuration.
    - **Threshold client** — prevents repeated messages with customizable expiration rules.
    - **APM client** — stores extra information in **APM** and adds a reference to the Telegram message for linking logs
      in **Kibana**.
- ⚡ **gRPC communication** — lightweight and efficient message transfer between clients and the server.
- 🩺 **Built-in health check** — verify that the server is running correctly.
- 🖥 **Command-line tools**:
    - `tg-notifier` — run the server.
    - `tg-notifier-healthcheck` — run a health check against the server.

---

## Usage

### Running the Server

The server can be configured with the following options:

| Config                | Type | Description                                     |
|-----------------------|------|-------------------------------------------------|
| `server_url`          | str  | gRPC server host (default: `localhost`)         |
| `server_port`         | int  | gRPC server port (default: `50051`)             |
| `server_max_workers`  | int  | Max workers for gRPC server                     |
| `service_max_threads` | int  | Max background threads for message sending      |
| `only_print`          | bool | If `True`, messages are printed instead of sent |
| `log_level`           | str  | Logging level (e.g., `INFO`, `DEBUG`)           |
| `log_file`            | str  | Path to log file. default log in stdout         |
| `config_file`         | str  | Path to a config file                           |


---



#### 1. Start the server using the CLI command

```bash
tg-notifier
```

Example:

```bash
tg-notifier --server_url 0.0.0.0 --server_port 50051 --server-max-workers 10 --log-level DEBUG
```



#### 2. Start in python



```python
from telegram_notifier.notifier_utils.config import NotifierConfig
from telegram_notifier.serve import serve

serve(
    config=NotifierConfig(
        server_url='localhost',
        server_port=50051,
        server_max_workers=10,
        service_max_threads=10,
        only_print=False,
    )
)
```



### Clients

#### 1. Simple Client

Send a message directly to Telegram:

```python
from telegram_notifier.clients import notifier_client

client = notifier_client.NotifierClient(
    server_url='localhost',
    server_port=50051,
    tg_bot_token='',
    tg_receiver_id=1
)
client.send_message_to_server('Hello from telegram-notifier!')
```

#### 2. Threshold Client

Avoid spamming repeated messages:

```python
from redis import Redis

from telegram_notifier.clients import notifier_client

client = notifier_client.ThresholdNotifierClient(
    server_url='localhost',
    server_port=50051,
    tg_bot_token='',
    tg_receiver_id=1,
    redis=Redis(host='localhost', port=6379, db=5, decode_responses=True),
    app_name='tg-notifier',
    process_name='web-server',
    developers_id=('@1234tg',),
)

client.send_message('hello world', expire=3600, mention_dev=True)  # 1 hour expiration
```

---

### Health Check

Verify that the server is running:

```bash
tg-notifier-healthcheck
```
