import socket
import threading
import json
from utils.output_rich import Rich

from core.base import Battle, Warrior, Mage, Assassin, Actions

LOGS_QUEUE = []


class GameServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 5555):
        self.host = host
        self.port = port
        self.is_running = False
        self.server_socket = None
        self.clients: list = []

        self.battle = None
        self.actions = {}
        self.lock = threading.Lock()

    def start(self) -> None:
        self.is_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)

        message = f"Сервер запущен на {self.host}:{self.port}"
        Rich.debug_log(message)
        LOGS_QUEUE.append(message)

        while self.is_running:
            try:
                self.server_socket.settimeout(1.0)
                conn, addr = self.server_socket.accept()
                with self.lock:
                    self.clients.append(conn)
                    LOGS_QUEUE.append(f"Игрок подключился: {addr}")

                    # Когда подключились оба, создаем бой
                    if len(self.clients) == 2:
                        # Для теста создаем Воина против Мага
                        # (Потом можно добавить выбор персонажей)
                        self.battle = Battle(Warrior(), Mage())

                        LOGS_QUEUE.append("Оба игрока на месте! Бой начинается.")
                        self._broadcast_state("Бой начался! Ваш ход.")

                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

            except socket.timeout:
                continue
            except OSError:
                break

    def handle_client(self, conn: socket.socket, addr: tuple) -> None:
        try:
            while self.is_running:
                data = conn.recv(1024)
                if not data:
                    break

                msg = json.loads(data.decode('utf-8'))

                if msg.get("type") == "action" and self.battle and not self.battle.is_over:
                    with self.lock:
                        action_str = msg.get("value")
                        self.actions[conn] = action_str
                        LOGS_QUEUE.append(f"Игрок {addr} выбрал: {action_str}")

                        if len(self.actions) == 2:
                            if len(self.clients) < 2:
                                self.actions.clear()
                                continue

                            p1_socket = self.clients[0]
                            p2_socket = self.clients[1]

                            act1_str = self.actions.get(p1_socket)
                            act2_str = self.actions.get(p2_socket)

                            # Конвертируем строки в Enum
                            act1 = Actions[act1_str]
                            act2 = Actions[act2_str]

                            # Вызываем реальный метод битвы!
                            result = self.battle.play_turn(act1, act2)

                            LOGS_QUEUE.append(f"Результат хода: {result}")
                            self._broadcast_state(result)

                            self.actions.clear()

        except Exception as e:
            LOGS_QUEUE.append(f"Ошибка с {addr}: {e}")
        finally:
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
                if conn in self.actions:
                    del self.actions[conn]
            conn.close()
            LOGS_QUEUE.append(f"Игрок {addr} отключился.")

    def _broadcast_state(self, message: str) -> None:
        """Отправляет клиентам текст и ТЕКУЩИЕ СТАТЫ игроков"""
        state = {
            "type": "result",
            "message": message,
            "p1": {"name": self.battle.char1.name, "hp": self.battle.char1.hp, "max_hp": self.battle.char1.max_hp},
            "p2": {"name": self.battle.char2.name, "hp": self.battle.char2.hp, "max_hp": self.battle.char2.max_hp},
            "is_over": self.battle.is_over
        }
        raw = json.dumps(state).encode('utf-8')
        for c in self.clients:
            try:
                c.sendall(raw)
            except Exception:
                pass

    def stop(self) -> None:
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            client.close()
        self.actions.clear()
        self.battle = None
        self.clients.clear()
        message = "Сервер остановлен."
        Rich.debug_log(message)
        LOGS_QUEUE.append(message)