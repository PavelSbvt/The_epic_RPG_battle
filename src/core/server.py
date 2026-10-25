import socket

from utils.output_rich import Rich



LOGS_QUEUE = []

class GameServer:
    """
    Класс для работы игрового сервера
    """

    def __init__(self, host: str = '0.0.0.0', port: int =5555):
        self.host: str = host
        self.port: int = port
        self.is_running: bool  = False
        self.server_socket = None
        self.clients: list = []


    def start(self) -> None:
        """
        Функция для запуска сервера

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
                self.clients.append(conn)

            except socket.timeout:
                continue
            except OSError:
                break


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
        self.clients.clear()

        message = "Сервер остановлен."
        Rich.debug_log(message)

        LOGS_QUEUE.append(message)
