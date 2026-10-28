from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QCloseEvent
from PyQt6.uic import loadUi

from utils.output_rich import Rich
from gui.utils.windows_animations import AnimationsManager
from gui.utils.windows_functions import (center_window,
    background_window_by_time_of_day)
from server.client import Client, CLIENT_LOGS_QUEUE
from gui.utils.update_gui import (update_progress_bar_animation,
    loading_window_img_click, update_animation_gradient)
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

        self.buttonLinkWithServer.setFont(Fonts.get_qfont("JetBrains_Regular", 12))
        self.buttonLinkWithServer.clicked.connect(lambda: Client.connect(self.buttonLinkWithServer))

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
