import socket
import threading
import json

from PyQt6.QtWidgets import QPushButton

from utils.output_rich import Rich

HOST = '127.0.0.1'
PORT = 5555

# Словарь для удобного ввода действий
ACTIONS_MAP = {
    "1": "BUFF",
    "2": "NORMAL_ATTACK",
    "3": "SPECIAL_ATTACK"
}

LOGS_QUEUE = []


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
                message = f"[СИСТЕМА]: {text}"
                Rich.info_log(message)
                LOGS_QUEUE.append(message)
            elif msg_type == "result":
                message_info = f"[РЕЗУЛЬТАТ ХОДА]: {text}"
                Rich.success_log(message_info)
                LOGS_QUEUE.append(message_info)

                message_guide ="\nВыберите действие (1 - Бафф, 2 - Обычная атака, 3 - Спец. атака):"
                Rich.debug_log(message_guide)
                LOGS_QUEUE.append(message_guide)
            else:
                else_message = f"\n[СООБЩЕНИЕ]: {text}"
                Rich.debug_log(else_message)
                LOGS_QUEUE.append(else_message)

        except json.JSONDecodeError:
            warning_message = "Получены данные в неизвестном формате."
            Rich.warning_log(warning_message)
            LOGS_QUEUE.append(warning_message)
        except Exception:
            print("\n")
            except_info = "Возникла ошибка. Соединение с сервером потеряно"
            Rich.log_error(except_info)
            LOGS_QUEUE.append(except_info)
            break


def main(button: QPushButton) -> None:
    """
    Главная функция клиента.

    :return: None
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))

        success_info_connect = f"Выполнено подключение к серверу: {HOST}:{PORT}"

        button.setText("Подключение выполнено")

        button.setStyleSheet("""
        QPushButton {
            background-color: #E5484D;
            color: #FFFFFF;           
            border: 1px solid #E5484D;
            border-radius: 10px;       
            padding: 4px 16px;
            font-size: 13px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #ED5F63;
            border: 1px solid #ED5F63;
        }
        
        QPushButton:pressed {
            background-color: #C93B40; 
            border: 1px solid #C93B40;
        }
        
        QPushButton:disabled {
            background-color: #4C525E; 
            color: #8A909C;
            border: 1px solid #4C525E;
        }
        """)

        Rich.success_log(success_info_connect)
        LOGS_QUEUE.append(success_info_connect)

    except ConnectionRefusedError:
        connecting_error_info = "Не удалось подключиться. Сервер запущен?"

        button.setText("Попробовать переподключиться")

        button.setFixedWidth(300)

        button.setStyleSheet("""
                    QPushButton {
                    background-color: #3574F0;
                    color: #FFFFFF;      
                    border: 1px solid #3574F0;
                    border-radius: 4px;    
                    padding: 4px 16px;        
                    font-size: 13px;
                    font-weight: 500;
                    border-radius: 10px;
                    }
                    
                    QPushButton:hover {
                    background-color: #4682F5;
                    border: 1px solid #4682F5;
                    }
                    
                    QPushButton:pressed {
                    background-color: #2B60CC;
                    border: 1px solid #2B60CC;
                    }
                    
                    QPushButton:disabled {
                    background-color: #4C525E;
                    color: #8A909C;
                    border: 1px solid #4C525E;
                }
                """)

        Rich.log_error(connecting_error_info)
        LOGS_QUEUE.append(connecting_error_info)

        return

    # Запускаем поток для чтения сообщений
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    Rich.debug_log("\nОжидание второго игрока...")
    LOGS_QUEUE.append("\nОжидание второго игрока...")

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
    LOGS_QUEUE.append("Клиент завершил работу.")
