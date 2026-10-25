from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt, QThread
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QCloseEvent
from PyQt6.uic import loadUi

from utils.output_rich import Rich
from core.server import GameServer
from gui.utils.windows_animations import AnimateManager
from gui.utils.windows_functions import center_window
from gui.utils.fonts import Fonts


class ServerThread(QThread):
    """
    Класс для вывода сервера на отдельный поток
    """

    def __init__(self, server_instance):
        super().__init__()
        self.server = server_instance


    def run(self) -> None:
        """
        Функция для запуска сервера в отдельном потоке

        :return: None
        """

        self.server.start()


    def stop(self) -> None:
        """
        Функция для остановки потока с сервером

        :return: None
        """

        self.server.stop()
        self.quit()
        self.wait()


class MainWindow(QWidget):
    """
    Класс загрузочного окна
    """

    closed = pyqtSignal()

    def __init__(self) -> None:
        """
        Конструктор класса
        """
        super().__init__()

        self.setObjectName("main_window")

        self.bg_path_check = ""

        self.close_window_animation = None

        self.server_thread = None

        Rich.enter_log("Показ главного окна.")

        ui_path = Path('src/gui/ui/main_window.ui').as_posix()
        loadUi(ui_path, self)

        self.labelTitle.setFont(Fonts.get_qfont("JetBrains_Regular", 14))
        self.buttonRunServer.setFont(Fonts.get_qfont("JetBrains_Medium", 8))

        self.buttonRunServer.clicked.connect(self.start_server)

        self.buttonStopServer.setVisible(False)
        self.buttonStopServer.clicked.connect(self.stop_server)


    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Обработка закрытия окна. Останавливаем сервер, если он запущен.

        :return: None
        """

        Rich.exit_log("Выход из приложения")

        if self.server_thread is not None and self.server_thread.isRunning():
            self.server_thread.stop()
        event.accept()


    def start_server(self) -> None:
        """
        Функция для запуска сервера

        :return: None
        """

        if self.server_thread is not None and self.server_thread.isRunning():
            Rich.warning_log("Сервер уже запущен!")
            return

        Rich.debug_log("Запуск сервера в фоновом режиме...")

        self.server_instance = GameServer()

        self.server_thread = ServerThread(self.server_instance)
        self.server_thread.start()

        self.buttonRunServer.setVisible(False)
        self.buttonStopServer.setVisible(True)


    def stop_server(self) -> None:
        """
        Функция для остановки сервера

        :return: None
        """

        if self.server_thread is not None and self.server_thread.isRunning():
            Rich.debug_log("Остановка сервера...")

            self.server_thread.stop()

            self.buttonRunServer.setEnabled(True)
            self.buttonRunServer.setVisible(True)
            self.buttonStopServer.setVisible(False)

            self.server_thread = None
            self.server_instance = None
