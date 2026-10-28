import socket
import threading
import json

from utils.output_rich import Rich

HOST = '127.0.0.1'
PORT = 5555

# Словарь для удобного ввода действий
ACTIONS_MAP = {
    "1": "BUFF",
    "2": "NORMAL_ATTACK",
    "3": "SPECIAL_ATTACK"
}


def receive_messages(sock: socket.socket) -> None:
    """
    Функция для получения сообщений от сервера в отдельном потоке.

    :param sock: Сокет клиента

    :return: None
    """

    while True:
        try:
            data = sock.recv(1024)
            if not data:
                Rich.warning_log("Сервер закрыл соединение.")
                break

            # Декодируем JSON-строку от сервера
            msg = json.loads(data.decode('utf-8'))

            # Проверяем тип сообщения
            msg_type = msg.get("type")
            text = msg.get("message", "")

            if msg_type == "system":
                Rich.info_log(f"[СИСТЕМА]: {text}")
            elif msg_type == "result":
                Rich.success_log(f"[РЕЗУЛЬТАТ ХОДА]: {text}")
                Rich.debug_log("\nВыберите действие (1 - Бафф, 2 - Обычная атака, 3 - Спец. атака):")
            else:
                Rich.debug_log(f"\n[СООБЩЕНИЕ]: {text}")

        except json.JSONDecodeError:
            Rich.warning_log("Получены данные в неизвестном формате.")
        except Exception:
            print("\n")
            Rich.log_error("Возникла ошибка. Соединение с сервером потеряно")
            break


def main() -> None:
    """
    Главная функция клиента.

    :return: None
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
        Rich.success_log(f"Выполнено подключение к серверу: {HOST}:{PORT}")
    except ConnectionRefusedError:
        Rich.log_error("Не удалось подключиться. Сервер запущен?")
        return

    # Запускаем поток для чтения сообщений
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    Rich.debug_log("\nОжидание второго игрока...")

    while True:
        # Запрашиваем у пользователя действие
        choice = Rich.input_data("Выберите действие (1 - Бафф, 2 - Обычная атака, 3 - Спец. атака, exit - выход)")

        if choice.lower() == 'exit':
            break

        if choice not in ACTIONS_MAP:
            Rich.warning_log("Неверный ввод. Введите 1, 2, 3 или exit.")
            continue

        # Формируем JSON для отправки на сервер
        action_name = ACTIONS_MAP[choice]
        msg = {
            "type": "action",
            "value": action_name
        }

        # Отправляем
        sock.sendall(json.dumps(msg).encode('utf-8'))
        Rich.debug_log(f"Вы отправили действие: {action_name}")

    sock.close()
    Rich.simple_log("Клиент завершил работу.")
