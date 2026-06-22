from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt


class LobbyRoomView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._is_ready = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # --- En-tête ---
        header_layout = QHBoxLayout()
        self.lobby_title = QLabel("Lobby")
        self.lobby_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #c0392b;")
        header_layout.addWidget(self.lobby_title)
        header_layout.addStretch()

        self.leave_btn = QPushButton("Quitter")
        self.leave_btn.setFixedSize(90, 34)
        self.leave_btn.setStyleSheet(
            "background-color: #7f8c8d; color: white; border-radius: 6px; font-size: 12px;"
        )
        self.leave_btn.clicked.connect(self.controller.leave_lobby)
        header_layout.addWidget(self.leave_btn)
        main_layout.addLayout(header_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #ddd;")
        main_layout.addWidget(sep)

        # --- Liste des joueurs ---
        players_label = QLabel("Joueurs dans le lobby :")
        players_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #555;")
        main_layout.addWidget(players_label)

        self.players_list = QListWidget()
        self.players_list.setStyleSheet(
            "background-color: white; border: 1px solid #ddd; border-radius: 6px; font-size: 13px;"
        )
        self.players_list.setMaximumHeight(200)
        main_layout.addWidget(self.players_list)

        # --- Boutons ---
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)

        self.ready_btn = QPushButton("✅  Prêt")
        self.ready_btn.setFixedHeight(42)
        self.ready_btn.setStyleSheet(
            "background-color: #27ae60; color: white; font-weight: bold; border-radius: 6px; font-size: 13px;"
        )
        self.ready_btn.clicked.connect(self.on_ready_clicked)
        actions_layout.addWidget(self.ready_btn)

        self.start_btn = QPushButton("🚀  Démarrer la partie")
        self.start_btn.setFixedHeight(42)
        self.start_btn.setStyleSheet(
            "background-color: #c0392b; color: white; font-weight: bold; border-radius: 6px; font-size: 13px;"
        )
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.controller.start_game)
        actions_layout.addWidget(self.start_btn)

        main_layout.addLayout(actions_layout)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        main_layout.addStretch()

    def update_lobby(self, lobby: dict):
        self.lobby_title.setText(f"Lobby  [{lobby.get('id', '')}]")
        self.players_list.clear()
        owner_sid = lobby.get("owner_sid", "")

        for sid, player in lobby.get("players", {}).items():
            username   = player.get("username", sid)
            is_ready   = player.get("is_ready", False)
            ready_icon = "✅" if is_ready else "⏳"
            owner_icon = " 👑" if sid == owner_sid else ""
            item = QListWidgetItem(f"{ready_icon}  {username}{owner_icon}")
            item.setData(Qt.UserRole, sid)
            self.players_list.addItem(item)

        # Activer start uniquement pour le owner
        try:
            my_sid  = self.controller.my_sid
            is_owner = owner_sid == my_sid
        except Exception:
            is_owner = False

        # En solo (owner seul), cacher le bouton Prêt et activer directement Démarrer
        player_count = len(lobby.get("players", {}))
        if is_owner:
            self.ready_btn.setVisible(player_count > 1)
            self.start_btn.setEnabled(True)
        else:
            self.ready_btn.setVisible(True)
            self.start_btn.setEnabled(False)

    def on_ready_clicked(self):
        self._is_ready = not self._is_ready
        self.controller.set_ready(self._is_ready)
        if self._is_ready:
            self.ready_btn.setText("❌  Pas prêt")
            self.ready_btn.setStyleSheet(
                "background-color: #e67e22; color: white; font-weight: bold; border-radius: 6px; font-size: 13px;"
            )
        else:
            self.ready_btn.setText("✅  Prêt")
            self.ready_btn.setStyleSheet(
                "background-color: #27ae60; color: white; font-weight: bold; border-radius: 6px; font-size: 13px;"
            )
