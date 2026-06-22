from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from view.login_view import LoginView
from view.lobby_list_view import LobbyListView
from view.lobby_room_view import LobbyRoomView
from view.game_view import GameView
from view.end_game_view import EndGameView

# Index des vues dans le QStackedWidget
IDX_LOGIN      = 0
IDX_LOBBY_LIST = 1
IDX_LOBBY_ROOM = 2
IDX_GAME       = 3
IDX_END_GAME   = 4


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("TUSMO")
        self.resize(720, 520)
        self.setStyleSheet("background-color: #f9f9f9; font-family: Segoe UI, Arial, sans-serif;")

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.login_view      = LoginView(controller)
        self.lobby_list_view = LobbyListView(controller)
        self.lobby_room_view = LobbyRoomView(controller)
        self.game_view       = GameView(controller)
        self.end_game_view   = EndGameView(controller)

        self.stacked.addWidget(self.login_view)       # 0
        self.stacked.addWidget(self.lobby_list_view)  # 1
        self.stacked.addWidget(self.lobby_room_view)  # 2
        self.stacked.addWidget(self.game_view)        # 3
        self.stacked.addWidget(self.end_game_view)    # 4

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def show_lobby_list_view(self):
        self.stacked.setCurrentIndex(IDX_LOBBY_LIST)

    def show_lobby_room_view(self):
        self.stacked.setCurrentIndex(IDX_LOBBY_ROOM)

    def show_game_view(self, data: dict):
        word_length = data.get("word_length", 5)
        first_char  = data.get("first_char", "")
        self.game_view.setup_grid(word_length, first_char)
        self.stacked.setCurrentIndex(IDX_GAME)

    def show_end_game_view(self, word: str, scores: list, has_won: bool):
        self.end_game_view.show_results(word, scores, has_won)
        self.stacked.setCurrentIndex(IDX_END_GAME)

    def show_login_view(self):
        self.login_view.reset()
        self.stacked.setCurrentIndex(IDX_LOGIN)

    # ------------------------------------------------------------------ #
    #  Erreurs                                                             #
    # ------------------------------------------------------------------ #

    def show_error(self, error_code: str, message: str):
        ERROR_MESSAGES = {
            "ALREADY_IN_LOBBY":    "Vous êtes déjà dans un lobby.",
            "NOT_IN_LOBBY":        "Vous n'êtes dans aucun lobby.",
            "LOBBY_NOT_FOUND":     "Lobby introuvable.",
            "LOBBY_FULL":          "Ce lobby est complet.",
            "NOT_OWNER":           "Seul le créateur peut effectuer cette action.",
            "GAME_ALREADY_STARTED":"La partie a déjà commencé.",
            "GAME_NOT_STARTED":    "La partie n'a pas encore commencé.",
            "NOT_ALL_READY":       "Tous les joueurs ne sont pas prêts.",
            "INVALID_GUESS":       "Proposition invalide.",
            "WORD_NOT_IN_DICT":    "Ce mot n'est pas dans le dictionnaire.",
            "WRONG_LENGTH":        "Le mot n'a pas la bonne longueur.",
            "GAME_OVER":           "Votre partie est déjà terminée.",
            "CONNECTION_ERROR":    "Impossible de se connecter au serveur.",
        }
        friendly = ERROR_MESSAGES.get(error_code, message or error_code)

        # Affichage contextuel selon la vue active
        idx = self.stacked.currentIndex()
        if idx == IDX_LOBBY_LIST:
            self.lobby_list_view.set_status(friendly, error=True)
        elif idx == IDX_GAME:
            self.game_view.set_status(friendly, error=True)
        else:
            QMessageBox.warning(self, "Erreur", friendly)
