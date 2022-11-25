#!/usr/bin/env python3

import sys

from PyQt6 import QtWidgets

from qt.client_main_ui import ClientMain
from settings.client_settings import SERVER
from modules.requester import Requester

# To compile resources from qrc
# pyside6-rcc resources.qrc | sed '0,/PySide6/s//PyQt6/' > resources.py


def main():
    app = QtWidgets.QApplication([])
    main_window = QtWidgets.QMainWindow()
    requester = Requester(SERVER)
    ui = ClientMain(main_window, requester)
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
