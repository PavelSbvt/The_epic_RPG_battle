import socket
import threading
import json

from PyQt6.QtWidgets import QPushButton
from utils.output_rich import Rich

PORT = 5555

CLIENT_LOGS_QUEUE = []

GAME_STATE = {
    "p1": {"name": "?", "hp": 0, "max_hp": 1},
    "p2": {"name": "?", "hp": 0, "max_hp": 1},
    "is_over": False,
    "my_player": None,
}


class GameClient:
    """
    Класс клиента для подключения к игровому серверу и отправки действий.
    """

    def __init__(self) -> None:
        self.sock: socket.socket | None = None
        self.is_connected: bool = False

    def connect(self, button: QPushButton, ip_address: str = '127.0.0.1') -> None:
        """
        Подключение к серверу.

        :param button: Кнопка подключения (для изменения её стиля и текста)
        :param ip_address: IP-адрес сервера (по умолчанию '127.0.0.1' для локального теста)

        :return: None
        """
        if self.is_connected:
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((ip_address, PORT))
            self.is_connected = True

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

            info = f"Выполнено подключение к серверу: {ip_address}:{PORT}"
            Rich.success_log(info)
            CLIENT_LOGS_QUEUE.append(info)

            # Запускаем фоновое чтение сообщений
            threading.Thread(target=self._receive_messages, daemon=True).start()

        except ConnectionRefusedError:
            info = f"Сервер по адресу {ip_address}:{PORT} не отвечает. Сервер запущен?"
            button.setText("Попробовать переподключиться")
            button.setFixedWidth(300)
            Rich.log_error(info)
            CLIENT_LOGS_QUEUE.append(info)

        except socket.gaierror:
            info = f"Неверный IP-адрес: {ip_address}"
            button.setText("Попробовать переподключиться")
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
                    CLIENT_LOGS_QUEUE.append("Сервер закрыл соединение.")
                    self.is_connected = False
                    break

                msg = json.loads(data.decode('utf-8'))
                msg_type = msg.get("type")
                text = msg.get("message", "")

                if msg_type == "you_are":
                    GAME_STATE["my_player"] = msg.get("player")
                    CLIENT_LOGS_QUEUE.append(f"Вы — Игрок {msg.get('player')}")
                    continue

                if msg_type == "system":
                    CLIENT_LOGS_QUEUE.append(f"[СИСТЕМА]: {text}")
                    continue

                if msg_type == "error":
                    CLIENT_LOGS_QUEUE.append(f"[ОШИБКА]: {text}")
                    continue

                if msg_type == "result":
                    # ВАЖНО: мутируем, а не пересоздаём, чтобы my_player не потерялся
                    GAME_STATE["p1"] = msg.get("p1", {"name": "?", "hp": 0, "max_hp": 1})
                    GAME_STATE["p2"] = msg.get("p2", {"name": "?", "hp": 0, "max_hp": 1})
                    GAME_STATE["is_over"] = msg.get("is_over", False)
                    CLIENT_LOGS_QUEUE.append(f"[РЕЗУЛЬТАТ ХОДА]: {text}")
                    continue

            except json.JSONDecodeError:
                CLIENT_LOGS_QUEUE.append("Ошибка: получены данные в неизвестном формате.")
            except Exception as e:
                CLIENT_LOGS_QUEUE.append(f"Ошибка соединения: {e}")
                self.is_connected = False
                break

    def _send_action(self, action_name: str) -> None:
        """
        Внутренний метод для отправки действия на сервер.

        :param action_name: Название действия (BUFF, NORMAL_ATTACK, SPECIAL_ATTACK)
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
        """Отправляет действие "Бафф"."""
        self._send_action("BUFF")

    def send_normal_attack(self) -> None:
        """Отправляет действие "Обычная атака"."""
        self._send_action("NORMAL_ATTACK")

    def send_special_attack(self) -> None:
        """Отправляет действие "Специальная атака"."""
        self._send_action("SPECIAL_ATTACK")

    def send_class_choice(self, class_name: str) -> None:
        """
        Отправляет серверу выбор класса персонажа.

        :param class_name: "Warrior" | "Mage" | "Assassin"
        :return: None
        """
        if not self.is_connected or not self.sock:
            CLIENT_LOGS_QUEUE.append("Нет подключения — выбор класса не отправлен")
            return
        try:
            self.sock.sendall(json.dumps({
                "type": "choose_class",
                "value": class_name,
            }).encode("utf-8"))
            CLIENT_LOGS_QUEUE.append(f"Выбран класс: {class_name}")
        except Exception as e:
            CLIENT_LOGS_QUEUE.append(f"Ошибка отправки класса: {e}")

    def disconnect(self) -> None:
        """Отключает клиента от сервера и закрывает сокет."""
        self.is_connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

        # Сбрасываем состояние игры
        GAME_STATE["p1"] = {"name": "?", "hp": 0, "max_hp": 1}
        GAME_STATE["p2"] = {"name": "?", "hp": 0, "max_hp": 1}
        GAME_STATE["is_over"] = False
        GAME_STATE["my_player"] = None

        CLIENT_LOGS_QUEUE.append("Вы отключились от сервера.")


Client = GameClient()