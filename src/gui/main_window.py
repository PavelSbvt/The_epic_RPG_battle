from pathlib import Path

from PyQt6.QtCore import (QPoint, QTimer, pyqtSignal, Qt,
    QThread, QPropertyAnimation, QEasingCurve)
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QCloseEvent
from PyQt6.uic import loadUi

from utils.output_rich import Rich
from core.server import GameServer, LOGS_QUEUE
from gui.utils.fonts import Fonts
from utils.create_shortcut import check_build


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

        # атрибут для хранения позиции мыши(x,y), объект класса qpoint
        self.drag_position: QPoint = QPoint()

        Rich.enter_log("Показ главного окна.")

        ui_path = Path('src/gui/ui/main_window.ui').as_posix()
        loadUi(ui_path, self)

        self.labelTitle.setFont(Fonts.get_qfont("JetBrains_Regular", 14))
        self.buttonRunServer.setFont(Fonts.get_qfont("JetBrains_Medium", 8))
        self.textEditForLogs.setFont(Fonts.get_qfont("JetBrains_Medium", 10))

        self.buttonRunServer.clicked.connect(self.start_server)

        self.buttonStopServer.setVisible(False)
        self.buttonStopServer.clicked.connect(self.stop_server)

        self.buttonRunServer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.buttonStopServer.setCursor(Qt.CursorShape.PointingHandCursor)

        self.tab_widget.setTabVisible(1, False)

        self.settings_path = Path("resources/images/icons/settings_pycharm_icon.png")
        self.settingsButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settingsButton.setStyleSheet(f"""
                        QPushButton {{
                            background-image: url({self.settings_path.as_posix()});
                            border: none;
                            background-repeat: no-repeat;
                            background-position: center;
                            background-color: transparent;
                            border-radius: 5px;
                        }}
                        QPushButton:hover {{
                            background-color: rgba(255, 255, 255, 0.08);
                        }}
                        QPushButton:pressed {{
                            background-color: rgba(255, 255, 255, 0.15);
                        }}
                    """)
        self.settingsButton.clicked.connect(self.open_settings_tab)

        self.tab_widget.setFont(Fonts.get_qfont("JetBrains_Medium", 8))

        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.check_logs)
        self.log_timer.start(100)

        self.labelShortcut.setFont(Fonts.get_qfont("JetBrains_Medium", 12))
        self.buttonCreateShortcut.setFont(Fonts.get_qfont("JetBrains_Medium", 10))

        self.buttonCreateShortcut.clicked.connect(check_build)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)


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
        Обработка закрытия окна. Запуск анимации прозрачности.

        :return: None
        """

        if getattr(self, "_is_closing", False):
            return

        self._is_closing = True
        event.ignore()

        Rich.exit_log("Выход из приложения")
        if self.server_thread is not None and self.server_thread.isRunning():
            self.server_thread.stop()

        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        self.fade_anim.finished.connect(self.close)

        self.fade_anim.start()


    def open_settings_tab(self) -> None:
        """
        Функция для открытия вкладки с настройками

        :return: None
        """

        self.tab_widget.setCurrentIndex(1)


    def start_server(self) -> None:
        """
        Функция для запуска сервера

        :return: None
        """

        if self.server_thread is not None and self.server_thread.isRunning():
            Rich.warning_log("Сервер уже запущен!")
            self.add_log("Сервер уже запущен!")
            return

        message = "Запуск сервера в фоновом режиме..."

        Rich.debug_log(message)
        self.add_log(message)

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
            message = "Остановка сервера..."

            Rich.debug_log(message)
            self.add_log(message)

            self.server_thread.stop()

            self.buttonRunServer.setEnabled(True)
            self.buttonRunServer.setVisible(True)
            self.buttonStopServer.setVisible(False)

            self.server_thread = None

            self.server_instance = None


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

        while LOGS_QUEUE:
            message = LOGS_QUEUE.pop(0)
            self.add_log(message)
