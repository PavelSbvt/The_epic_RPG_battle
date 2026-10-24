import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


if __name__ == "__main__":
    App = QApplication(sys.argv)

    MainWin = MainWindow()
    MainWin.setWindowTitle("Server")
    MainWin.show()

    sys.exit(App.exec())
