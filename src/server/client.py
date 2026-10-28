import socket
import threading
import json

from PyQt6.QtWidgets import QPushButton
from utils.output_rich import Rich

HOST = '127.0.0.1'
PORT = 5555

# Очередь для логов (чтобы UI мог их забирать)
CLIENT_LOGS_QUEUE = []


class GameClient:
    """
    Класс клиента для подключения к игровому серверу и отправки действий.
    """

    def __init__(self) -> None:
        self.sock: socket.socket | None = None
        self.is_connected: bool = False

    def connect(self, button: QPushButton) -> None:
        """
        Подключение к серверу.

        :param button: Кнопка подключения (для изменения её стиля и текста)

        :return: None
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((HOST, PORT))
            self.is_connected = True

            # Меняем кнопку на "успешно"
            button.setText("Подключение выполнено")
            button.setEnabled(False)
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
                QPushButton:disabled { 
                    background-color: #4C525E; 
                    color: #8A909C; 
                    border: 1px solid #4C525E; 
                }
            """)

            info = f"Выполнено подключение к серверу: {HOST}:{PORT}"
            Rich.success_log(info)
            CLIENT_LOGS_QUEUE.append(info)

            # Запускаем фоновое чтение сообщений
            threading.Thread(target=self._receive_messages, daemon=True).start()

        except ConnectionRefusedError:
            info = "Не удалось подключиться. Сервер запущен?"
            button.setText("Попробовать переподключиться")
            button.setFixedWidth(300)
            Rich.log_error(info)
            CLIENT_LOGS_QUEUE.append(info)

    def _receive_messages(self) -> None:
        """
        Читает сообщения от сервера в фоновом потоке.
        """
        while self.is_connected and self.sock:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break

                msg = json.loads(data.decode('utf-8'))
                msg_type = msg.get("type")
                text = msg.get("message", "")

                if msg_type == "system":
                    CLIENT_LOGS_QUEUE.append(f"[СИСТЕМА]: {text}")
                elif msg_type == "result":
                    CLIENT_LOGS_QUEUE.append(f"[РЕЗУЛЬТАТ ХОДА]: {text}")
                    CLIENT_LOGS_QUEUE.append("Выберите действие:")
                else:
                    CLIENT_LOGS_QUEUE.append(f"[СООБЩЕНИЕ]: {text}")

            except Exception as e:
                CLIENT_LOGS_QUEUE.append(f"Ошибка соединения: {e}")
                self.is_connected = False
                break

    def _send_action(self, action_name: str) -> None:
        """
        Внутренний метод для отправки действия на сервер.
        (Защищен от прямого вызова извне, хотя в Python это не строго).

        :param action_name: Название действия

        :return: None
        """
        if not self.is_connected or not self.sock:
            CLIENT_LOGS_QUEUE.append("Нет подключения к серверу!")
            return

        msg = {
            "type": "action",
            "value": action_name
        }
        try:
            self.sock.sendall(json.dumps(msg).encode('utf-8'))
            CLIENT_LOGS_QUEUE.append(f"Вы отправили: {action_name}")
        except Exception as e:
            CLIENT_LOGS_QUEUE.append(f"Ошибка отправки: {e}")

    def send_buff(self) -> None:
        """
        Отправляет действие "Бафф".
        """
        self._send_action("BUFF")

    def send_normal_attack(self) -> None:
        """
        Отправляет действие "Обычная атака".
        """
        self._send_action("NORMAL_ATTACK")

    def send_special_attack(self) -> None:
        """
        Отправляет действие "Специальная атака".
        """
        self._send_action("SPECIAL_ATTACK")

    def disconnect(self) -> None:
        """
        Отключает клиента от сервера и закрывает сокет.
        """
        self.is_connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
        CLIENT_LOGS_QUEUE.append("Вы отключились от сервера.")


# Создаем глобальный экземпляр клиента
Client = GameClient()