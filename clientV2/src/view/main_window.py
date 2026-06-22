from PySide6.QtWidgets import QMainWindow, QStackedWidget
from view.login_view import LoginView
from view.lobby_list_view import LobbyListView


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('TUSMO - Lobby')
        self.resize(600, 400)
        self.setStyleSheet('background-color: #FFC0CB;')

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Vue 0 : Login
        self.login_view = LoginView(self.controller)
        self.stacked_widget.addWidget(self.login_view)

        # Vue 1 : Liste des Lobbies
        self.lobby_view = LobbyListView(self.controller)
        self.stacked_widget.addWidget(self.lobby_view)

    def show_lobby_list_view(self):
        """Bascule vers l'écran des lobbies"""
        self.stacked_widget.setCurrentIndex(1)
