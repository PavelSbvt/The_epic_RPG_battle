import socket
import threading

from utils.output_rich import Rich


HOST = '0.0.0.0'   # слушаем на всех интерфейсах
PORT = 5555        # любой свободный порт

clients = []       # список подключённых клиентов

def handle_client(conn, addr):
    Rich.success_log(f"К серверу подключился: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            Rich.print_message(message, addr)

            # Пересылаем всем остальным клиентам
            for c in clients:
                if c != conn:
                    try:
                        c.sendall(f"[{addr}] {message}".encode('utf-8'))
                    except Exception:
                        pass
    except ConnectionResetError:
        pass
    finally:
        Rich.simple_log(f"Пользователь {addr} отключился от сервера")
        clients.remove(conn)
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(2)   # ждём максимум 2 клиента
    Rich.success_log(f"Сервер запущен на {HOST}:{PORT}.")

    while True:
        conn, addr = server.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()