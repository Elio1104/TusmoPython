import sys
import os

# Ajout du dossier courant au path pour les imports relatifs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from PySide6.QtWidgets import QApplication
from view.main_window import MainWindow
from controller.game_controller import GameController

def main():
    app = QApplication(sys.argv)

    controller = GameController()
    window = MainWindow(controller)
    controller.set_view(window)

    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
