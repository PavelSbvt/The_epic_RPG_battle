import sys
from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QCloseEvent, QColor
from PyQt6.uic import loadUi

from utils.output_rich import Rich
from gui.utils.windows_animations import AnimationsManager
from server.client import Client, CLIENT_LOGS_QUEUE
from core.interface import (
    MainWindow, QPalette,
    ACCENT, TEXT, PANEL_BG,
    CARD_BG, DARK_BG)
from gui.utils.fonts import Fonts


class ClientWindow(QWidget):
    """
    Класс окна клиента
    """

    closed = pyqtSignal()

    def __init__(self) -> None:
        """
        Конструктор класса
        """
        super().__init__()

        self.setObjectName("client_window")

        self.close_window_animation = None

        Rich.enter_log("Показ окна клиента.")

        ui_path = Path('src/gui/ui/client_window.ui').as_posix()
        loadUi(ui_path, self)

        self.labelTitleClient.setFont(Fonts.get_qfont("JetBrains_Regular", 12))
        self.textEditForLogs.setFont(Fonts.get_qfont("JetBrains_Regular", 8))

        self.inputIP.setFont(Fonts.get_qfont("JetBrains_Regular", 10))

        self.inputIP.setPlaceholderText("Введите IP сервера (например, 192.168.1.5)")

        self.buttonLinkWithServer.setFont(Fonts.get_qfont("JetBrains_Regular", 12))
        self.buttonLinkWithServer.clicked.connect(self.try_connect)

        self.buttonRunGame.clicked.connect(self.open_main_game_window)

        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.check_logs)
        self.log_timer.start(100)

        self.drag_position: QPoint = QPoint()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def mousePressEvent(self, event) -> None:
        """
        Обработчик события нажатия кнопки мыши.

        :param event: Принимает event - объект события, содержащий информацию о нажатии
        (какая кнопка, координаты и т.д.).

        :return: None
        """

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        """
        Обработчик события движения мыши.

        :param event: Принимает event - объект события, содержащий информацию о нажатии
        (какая кнопка, координаты и т.д.).

        :return: None
        """

        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Функция, вызывающаяся при закрытии окна.

        :param event: событие закрытия окна

        :return: None
        """

        if getattr(self, "_is_closing", False):
            event.accept()
            return

        Client.disconnect()

        Rich.exit_log("Выход из приложения - закрытие главного окна")

        self._is_closing = True

        event.ignore()

        Rich.debug_log("Запуск анимации исчезновения окна")

        self.close_anim = AnimationsManager.animation_of_window_disappearing(self, 265)

    def try_connect(self) -> None:
        """
        Функция для попытки подключения к серверу по IP-адресу из поля ввода.
        """
        # Берем IP из поля ввода.
        # Если поле пустое, используем 127.0.0.1 для теста на одном компьютере.
        if hasattr(self, 'inputIP'):
            ip = self.inputIP.text().strip()
        else:
            ip = "127.0.0.1"  # Если поля нет, подключаемся локально

        if not ip:
            ip = "127.0.0.1"

        Client.connect(self.buttonLinkWithServer, ip_address=ip)

    def open_main_game_window(self) -> None:
        """
        Функция открытия основного окна игры
        :return: None
        """

        self.game_window = MainWindow()

        self.game_window.show()

        # self.hide()

    def add_log(self, message: str) -> None:
        """
        Функция для добавления логов для пользователя в TextEdit в окне сервера.
        Принимает текст лога и добавляет этот его в TextEdit

        :param message: str - принимает сообщение лога

        :return: None.
        """

        self.textEditForLogs.append(message)

    def check_logs(self) -> None:
        """
        Забирает сообщения из очереди и пишет их в TextEdit

        :return: None.
        """

        while CLIENT_LOGS_QUEUE:
            message = CLIENT_LOGS_QUEUE.pop(0)
            self.add_log(message)
