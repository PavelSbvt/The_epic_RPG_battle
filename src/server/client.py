import socket
import threading

from utils.output_rich import Rich


HOST = '127.0.0.1'
PORT = 5555

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print("\n[Сообщение]:", data.decode('utf-8'))

        except Exception:
            print("\n")
            Rich.log_error("Возникла ошибка. Соединение с сервером потеряно")
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    Rich.success_log(f"Выполнено подключение к серверу: {HOST}:{PORT}")

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        msg = Rich.input_data("Введите сообщение")
        if msg.lower() == 'exit':
            break
        sock.sendall(msg.encode('utf-8'))

    sock.close()


if __name__ == "__main__":
    main()