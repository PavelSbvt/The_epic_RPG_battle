import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

from gui.main_window import MainWindow
from utils.output_rich import Rich


if __name__ == "__main__":
    App = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/epic-rpg-server-icon.ico')
    App.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))

    MainWin = MainWindow()
    MainWin.setWindowTitle("Server")

    MainWin.setWindowOpacity(0.0)

    MainWin.show()

    Rich.enter_log("Показ главного окна")

    fade_in = QPropertyAnimation(MainWin, b"windowOpacity")
    fade_in.setDuration(250)
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)
    fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
    fade_in.start()

    MainWin.fade_in_anim = fade_in

    sys.exit(App.exec())
