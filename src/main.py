import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from gui.main_window import MainWindow


if __name__ == "__main__":
    App = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/epic-rpg-server-icon.ico')
    App.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))

    MainWin = MainWindow()
    MainWin.setWindowTitle("Server")
    MainWin.show()

    sys.exit(App.exec())
