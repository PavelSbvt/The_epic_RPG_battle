import socket
import threading
import json

from utils.output_rich import Rich



LOGS_QUEUE = []

class GameServer:
    """
    Класс для работы игрового сервера
    """

    def __init__(self, host: str = '0.0.0.0', port: int =5555):
        """
        Конструктор класса GameServer

        :param host: IP-адрес для прослушивания (по умолчанию '0.0.0.0')
        :param port: Порт для прослушивания (по умолчанию 5555)

        :return: None
        """

        self.host: str = host
        self.port: int = port
        self.is_running: bool = False
        self.server_socket = None
        self.clients: list = []

        self.battle = None
        self.actions = {}  # Словарь для хранения действий игроков: {сокет: действие}
        self.lock = threading.Lock()  # Защита от одновременного доступа


    def start(self) -> None:
        """
        Функция для запуска сервера и прослушивания подключений

        :return: None
        """

        self.is_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)

        message = f"Сервер запущен на {self.host}:{self.port}"

        Rich.debug_log(message)
        LOGS_QUEUE.append(message)

        # Главный цикл сервера
        while self.is_running:
            try:
                self.server_socket.settimeout(1.0)
                conn, addr = self.server_socket.accept()
                with self.lock:
                    self.clients.append(conn)
                    LOGS_QUEUE.append(f"Игрок подключился: {addr}")

                    if len(self.clients) == 2:
                        # вместо заглушки будет примерно
                        # это: self.battle = Battle(Warrior(), Mage())
                        self.battle = "MockBattle"  # Заглушка для теста
                        LOGS_QUEUE.append("Оба игрока на месте! Бой начинается.")
                        self.broadcast(
                            {"type": "system", "message": "Бой начался! Ваш ход."})

                # Запускаем отдельный поток для каждого клиента
                threading.Thread(
                    target=self.handle_client, args=(conn, addr), daemon=True).start()

            except socket.timeout:
                continue
            except OSError:
                break


    def handle_client(self, conn: socket.socket, addr: tuple) -> None:
        """
        Слушает конкретного клиента и обрабатывает его сообщения

        :param conn: Сокет подключенного клиента
        :param addr: Кортеж с IP-адресом и портом клиента (host, port)

        :return: None
        """

        try:
            while self.is_running:
                data = conn.recv(1024)
                if not data:
                    break

                msg = json.loads(data.decode('utf-8'))

                # Если клиент прислал действие
                if msg.get("type") == "action" and self.battle:
                    with self.lock:
                        self.actions[conn] = msg.get("value")
                        LOGS_QUEUE.append(f"Игрок {addr} выбрал: {msg.get('value')}")

                        # Если оба сделали ход
                        if len(self.actions) == 2:
                            # Получаем действия в правильном порядке
                            # (кто первый подключился,
                            # действия того будут исполняться первыми)
                            p1_socket = self.clients[0]
                            p2_socket = self.clients[1]

                            act1 = self.actions.get(p1_socket)
                            act2 = self.actions.get(p2_socket)

                            # потом будет: result = self.battle.play_turn(act1, act2)
                            result = f"Игрок 1 сделал {act1}, Игрок 2 сделал {act2}"

                            LOGS_QUEUE.append(f"Результат хода: {result}")
                            self.broadcast({"type": "result", "message": result})

                            # Очищаем действия для следующего хода
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


    def broadcast(self, message: dict) -> None:
        """
        Отправляет сообщение всем подключенным клиентам

        :param message: Словарь с сообщением (будет преобразован в JSON)

        :return: None
        """

        raw = json.dumps(message).encode('utf-8')
        for c in self.clients:
            try:
                c.sendall(raw)
            except Exception:
                pass


    def stop(self) -> None:
        """
        Функция для остановки сервера

        :return: None
        """

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
