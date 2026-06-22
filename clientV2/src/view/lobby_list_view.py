from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget, QLabel, QListWidgetItem
from PySide6.QtCore import Qt

class LobbyListView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Layout Principal Horizontal
        main_layout = QHBoxLayout(self)

        # --- Partie GAUCHE : Actions ---
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignTop)
        
        self.create_btn = QPushButton("Créer un Lobby")
        self.create_btn.setFixedSize(150, 50)
        self.create_btn.setStyleSheet("background-color: white; font-weight: bold;")
        self.create_btn.clicked.connect(self.controller.create_lobby)
        
        left_panel.addWidget(self.create_btn)
        main_layout.addLayout(left_panel, 1) # Poids 1

        # --- Partie DROITE : Liste des lobbies ---
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Lobbies disponibles :"))
        
        self.lobby_list_widget = QListWidget()
        self.lobby_list_widget.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")
        right_panel.addWidget(self.lobby_list_widget)
        
        # Bouton pour rejoindre le lobby sélectionné
        self.join_btn = QPushButton("Rejoindre")
        self.join_btn.clicked.connect(self.on_join_clicked)
        right_panel.addWidget(self.join_btn)
        
        main_layout.addLayout(right_panel, 3) # Poids 3 (plus large)

    def update_lobbies(self, lobbies):
        """Met à jour la liste affichée"""
        self.lobby_list_widget.clear()
        for lobby in lobbies:
            # Formatage : [ID] - X joueurs
            item_text = f"Lobby: {lobby['id']} | Joueurs: {lobby['players']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, lobby['id']) # On stocke l'ID
            self.lobby_list_widget.addItem(item)

    def on_join_clicked(self):
        current_item = self.lobby_list_widget.currentItem()
        if current_item:
            lobby_id = current_item.data(Qt.UserRole)
            self.controller.join_lobby(lobby_id)
