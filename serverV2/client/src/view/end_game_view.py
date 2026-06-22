from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class EndGameView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(16)
        main_layout.setAlignment(Qt.AlignCenter)

        # --- Titre ---
        self.result_label = QLabel("Partie terminée !")
        self.result_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(22)
        font.setBold(True)
        self.result_label.setFont(font)
        self.result_label.setStyleSheet("color: #c0392b;")
        main_layout.addWidget(self.result_label)

        # --- Mot de la partie ---
        self.word_label = QLabel("")
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet("font-size: 16px; color: #555;")
        main_layout.addWidget(self.word_label)

        # --- Séparateur ---
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #ddd;")
        main_layout.addWidget(sep)

        # --- Tableau des scores ---
        scores_label = QLabel("Classement")
        scores_label.setAlignment(Qt.AlignCenter)
        scores_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        main_layout.addWidget(scores_label)

        self.scores_table = QTableWidget()
        self.scores_table.setColumnCount(3)
        self.scores_table.setHorizontalHeaderLabels(["Joueur", "Résultat", "Essais"])
        self.scores_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scores_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.scores_table.setSelectionMode(QTableWidget.NoSelection)
        self.scores_table.setStyleSheet(
            "background-color: white; border: 1px solid #ddd; border-radius: 6px; font-size: 13px;"
        )
        self.scores_table.setMaximumHeight(220)
        main_layout.addWidget(self.scores_table)

        # --- Boutons ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.replay_btn = QPushButton("🔄  Rejouer")
        self.replay_btn.setFixedHeight(44)
        self.replay_btn.setStyleSheet(
            "background-color: #27ae60; color: white; font-weight: bold; "
            "border-radius: 6px; font-size: 14px;"
        )
        self.replay_btn.clicked.connect(self.on_replay)
        btn_layout.addWidget(self.replay_btn)

        self.leave_btn = QPushButton("🚪  Quitter le lobby")
        self.leave_btn.setFixedHeight(44)
        self.leave_btn.setStyleSheet(
            "background-color: #7f8c8d; color: white; font-weight: bold; "
            "border-radius: 6px; font-size: 14px;"
        )
        self.leave_btn.clicked.connect(self.controller.leave_lobby)
        btn_layout.addWidget(self.leave_btn)

        main_layout.addLayout(btn_layout)

    def show_results(self, word: str, scores: list, has_won: bool):
        """Affiche les résultats de fin de partie."""
        if has_won:
            self.result_label.setText("🎉 Bravo, vous avez gagné !")
            self.result_label.setStyleSheet("color: #27ae60; font-size: 22px; font-weight: bold;")
        else:
            self.result_label.setText("😞 Perdu !")
            self.result_label.setStyleSheet("color: #c0392b; font-size: 22px; font-weight: bold;")

        self.word_label.setText(f"Le mot était : {word.upper()}")

        self.scores_table.setRowCount(len(scores))
        for row, score in enumerate(scores):
            username_item = QTableWidgetItem(score.get("username", "?"))
            username_item.setTextAlignment(Qt.AlignCenter)

            result_text = "✅ Gagné" if score.get("has_won") else "❌ Perdu"
            result_item = QTableWidgetItem(result_text)
            result_item.setTextAlignment(Qt.AlignCenter)
            if score.get("has_won"):
                result_item.setForeground(Qt.darkGreen)
            else:
                result_item.setForeground(Qt.red)

            tries_item = QTableWidgetItem(str(score.get("guesses_used", 0)))
            tries_item.setTextAlignment(Qt.AlignCenter)

            self.scores_table.setItem(row, 0, username_item)
            self.scores_table.setItem(row, 1, result_item)
            self.scores_table.setItem(row, 2, tries_item)

        # Masquer le bouton rejouer si pas owner
        lobby = self.controller.current_lobby
        is_owner = False
        if lobby:
            try:
                is_owner = lobby.get("owner_sid") == self.controller.sio.get_sid()
            except Exception:
                pass
        self.replay_btn.setVisible(is_owner)

    def on_replay(self):
        self.controller.replay()
