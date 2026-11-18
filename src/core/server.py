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

        self.classes = {}
        self.players_ready = {}

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
                        p1_sock, p2_sock = self.clients[0], self.clients[1]
                        self._send_to(p1_sock, {"type": "you_are", "player": 1})
                        self._send_to(p2_sock, {"type": "you_are", "player": 2})
                        LOGS_QUEUE.append("Оба игрока на месте! Выберите класс.")
                        self._broadcast_state("Выберите класс персонажа.")

                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

            except socket.timeout:
                continue
            except OSError:
                break

    def _send_to(self, conn, payload: dict) -> None:
        try:
            conn.sendall(json.dumps(payload).encode('utf-8'))
        except Exception:
            pass

    def handle_client(self, conn: socket.socket, addr: tuple) -> None:
        try:
            while self.is_running:
                data = conn.recv(1024)
                if not data:
                    break

                msg = json.loads(data.decode('utf-8'))

                if msg.get("type") == "choose_class" and not self.battle:
                    with self.lock:
                        cls_name = msg.get("value")
                        if cls_name not in ("Warrior", "Mage", "Assassin"):
                            continue
                        self.classes[conn] = cls_name
                        self.players_ready[conn] = True
                        LOGS_QUEUE.append(f"{addr} выбрал класс {cls_name}")

                        # Оба выбрали — создаём бой
                        if len(self.classes) == 2 and len(self.clients) == 2:
                            p1_sock, p2_sock = self.clients[0], self.clients[1]
                            c1 = self._make_char(self.classes[p1_sock])
                            c2 = self._make_char(self.classes[p2_sock])
                            self.battle = Battle(c1, c2)
                            LOGS_QUEUE.append(f"Бой: {c1.name} vs {c2.name}")
                            self._broadcast_state("Бой начался! Ваш ход.")
                    continue

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

                            # Вызываем реальный метод битвы
                            result = self.battle.play_turn(act1, act2)

                            LOGS_QUEUE.append(f"Результат хода: {result}")

                            if self.battle.is_over:
                                # 1) сначала показать финал (battle ещё жив)
                                self._broadcast_state(result)
                                # 2) потом сбросить
                                self.battle = None
                                self.classes.clear()
                                self.actions.clear()
                                # 3) и пригласить выбрать класс заново
                                self._broadcast_state("Бой окончен. Выберите класс для новой игры.")
                            else:
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

                self.classes.pop(conn, None)
                self.players_ready.pop(conn, None)

            conn.close()
            LOGS_QUEUE.append(f"Игрок {addr} отключился.")

    def _make_char(self, name: str):
        return {"Warrior": Warrior, "Mage": Mage, "Assassin": Assassin}[name]()

    def _broadcast_state(self, message: str) -> None:
        if self.battle is None:
            state = {
                "type": "result",
                "message": message,
                "p1": {"name": "?", "hp": 0, "max_hp": 0},
                "p2": {"name": "?", "hp": 0, "max_hp": 0},
                "is_over": False,
            }
        else:
            state = {
                "type": "result",
                "message": message,
                "p1": {"name": self.battle.char1.name, "hp": self.battle.char1.hp, "max_hp": self.battle.char1.max_hp},
                "p2": {"name": self.battle.char2.name, "hp": self.battle.char2.hp, "max_hp": self.battle.char2.max_hp},
                "is_over": self.battle.is_over,
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
        self.classes.clear()
        self.players_ready.clear()
        self.battle = None
        self.clients.clear()
        message = "Сервер остановлен."
        Rich.debug_log(message)
        LOGS_QUEUE.append(message)