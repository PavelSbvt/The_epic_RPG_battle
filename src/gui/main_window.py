from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt, QThread
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.uic import loadUi

from utils.output_rich import Rich
from core.server import main
from gui.utils.windows_animations import AnimateManager
from gui.utils.windows_functions import center_window
from gui.utils.fonts import Fonts


class ServerThread(QThread):
    def run(self):
        main()


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


    def start_server(self):
        """
        Запуск сервера в отдельном потоке
        """

        if self.server_thread is not None and self.server_thread.isRunning():
            Rich.enter_log("Сервер уже запущен!")
            return

        Rich.enter_log("Запуск сервера в фоновом режиме...")

        self.server_thread = ServerThread()
        self.server_thread.start()

        self.buttonRunServer.setEnabled(False)
