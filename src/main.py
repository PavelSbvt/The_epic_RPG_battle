import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from gui.main_window import MainWindow
from gui.utils.windows_animations import AnimationsManager
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

    MainWin.fade_in_anim = AnimationsManager.window_appearance_animation(MainWin, 320)

    sys.exit(App.exec())
