from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QListWidget, QLabel, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt


class LobbyListView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # --- Panneau GAUCHE ---
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignTop)
        left_panel.setSpacing(10)

        title = QLabel("TUSMO")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #c0392b;")
        left_panel.addWidget(title)

        self.create_btn = QPushButton("➕  Créer un Lobby")
        self.create_btn.setFixedHeight(44)
        self.create_btn.setStyleSheet(
            "background-color: #c0392b; color: white; font-weight: bold; "
            "border-radius: 6px; font-size: 13px;"
        )
        self.create_btn.clicked.connect(self.controller.create_lobby)
        left_panel.addWidget(self.create_btn)

        hint = QLabel("Liste mise à jour\nautomatiquement")
        hint.setStyleSheet("color: #aaa; font-size: 11px;")
        left_panel.addWidget(hint)

        left_frame = QFrame()
        left_frame.setLayout(left_panel)
        left_frame.setFixedWidth(180)
        main_layout.addWidget(left_frame)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #ddd;")
        main_layout.addWidget(sep)

        # --- Panneau DROIT ---
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)

        header = QLabel("Lobbies disponibles")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #333;")
        right_panel.addWidget(header)

        self.lobby_list_widget = QListWidget()
        self.lobby_list_widget.setStyleSheet(
            "background-color: white; border: 1px solid #ddd; "
            "border-radius: 6px; padding: 4px; font-size: 13px;"
        )
        self.lobby_list_widget.setAlternatingRowColors(True)
        right_panel.addWidget(self.lobby_list_widget)

        self.join_btn = QPushButton("Rejoindre le lobby sélectionné")
        self.join_btn.setFixedHeight(40)
        self.join_btn.setStyleSheet(
            "background-color: #2980b9; color: white; font-weight: bold; "
            "border-radius: 6px; font-size: 13px;"
        )
        self.join_btn.clicked.connect(self.on_join_clicked)
        right_panel.addWidget(self.join_btn)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        right_panel.addWidget(self.status_label)

        main_layout.addLayout(right_panel, 1)

    def update_lobbies(self, lobbies: list):
        self.lobby_list_widget.clear()
        if not lobbies:
            placeholder = QListWidgetItem("Aucun lobby disponible...")
            placeholder.setFlags(Qt.NoItemFlags)
            placeholder.setForeground(Qt.gray)
            self.lobby_list_widget.addItem(placeholder)
            return
        for lobby in lobbies:
            status = "🟢 En jeu" if lobby.get("is_active") else "🟡 En attente"
            text = f"[{lobby['id']}]  {lobby['players_count']}/{lobby.get('max_players', 8)} joueurs  —  {status}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, lobby["id"])
            self.lobby_list_widget.addItem(item)

    def on_join_clicked(self):
        current = self.lobby_list_widget.currentItem()
        if current and current.flags() != Qt.NoItemFlags:
            self.controller.join_lobby(current.data(Qt.UserRole))
        else:
            self.set_status("Sélectionnez un lobby d'abord.", error=True)

    def set_status(self, message: str, error: bool = False):
        color = "#e74c3c" if error else "#27ae60"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.status_label.setText(message)
