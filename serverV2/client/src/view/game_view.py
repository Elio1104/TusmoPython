from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGridLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

CELL_SIZE = 52
MAX_TRIES = 6

COLOR_MAP = {
    "green":  ("#27ae60", "white"),
    "yellow": ("#f39c12", "white"),
    "gray":   ("#95a5a6", "white"),
    "empty":  ("white",   "#333"),
}


class LetterCell(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(CELL_SIZE, CELL_SIZE)
        self.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.setFont(font)
        self.set_state("empty", "")

    def set_state(self, color: str, letter: str):
        bg, fg = COLOR_MAP.get(color, COLOR_MAP["empty"])
        self.setStyleSheet(
            f"background-color: {bg}; color: {fg}; "
            f"border: 2px solid #bbb; border-radius: 6px;"
        )
        self.setText(letter.upper())


class GameView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller   = controller
        self.word_length  = 0
        self.current_row  = 0
        self.cells        = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)
        main_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("TUSMO")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #c0392b;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 13px; color: #555;")
        main_layout.addWidget(self.info_label)

        self.grid_frame  = QFrame()
        self.grid_layout = QGridLayout(self.grid_frame)
        self.grid_layout.setSpacing(6)
        main_layout.addWidget(self.grid_frame, alignment=Qt.AlignCenter)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.guess_input = QLineEdit()
        self.guess_input.setPlaceholderText("Votre mot...")
        self.guess_input.setFixedHeight(40)
        self.guess_input.setStyleSheet(
            "border: 2px solid #c0392b; border-radius: 6px; "
            "padding: 4px 10px; font-size: 15px; font-weight: bold;"
        )
        self.guess_input.returnPressed.connect(self.on_submit_guess)
        input_layout.addWidget(self.guess_input)

        self.submit_btn = QPushButton("Valider")
        self.submit_btn.setFixedSize(90, 40)
        self.submit_btn.setStyleSheet(
            "background-color: #c0392b; color: white; font-weight: bold; "
            "border-radius: 6px; font-size: 13px;"
        )
        self.submit_btn.clicked.connect(self.on_submit_guess)
        input_layout.addWidget(self.submit_btn)

        main_layout.addLayout(input_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 13px; color: #e74c3c;")
        main_layout.addWidget(self.status_label)

    def setup_grid(self, word_length: int, first_char: str = ""):
        self.word_length = word_length
        self.current_row = 0
        self.cells       = []

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for row in range(MAX_TRIES):
            row_cells = []
            for col in range(word_length):
                cell = LetterCell()
                self.grid_layout.addWidget(cell, row, col)
                row_cells.append(cell)
            self.cells.append(row_cells)

        if first_char and self.cells:
            self.cells[0][0].set_state("green", first_char)

        self.guess_input.setMaxLength(word_length)
        self.guess_input.setEnabled(True)
        self.submit_btn.setEnabled(True)
        self.info_label.setText(
            f"Mot de {word_length} lettres — commence par '{first_char.upper()}'"
        )

    def display_guess_result(self, result: dict):
        if self.current_row >= MAX_TRIES:
            return

        feedback  = result.get("feedback", [])
        row_cells = self.cells[self.current_row]

        for col, item in enumerate(feedback):
            if col < len(row_cells):
                row_cells[col].set_state(item.get("color", "gray").lower(), item.get("char", ""))

        self.current_row += 1
        self.guess_input.clear()

        if result.get("is_correct"):
            self.status_label.setText("🎉 Bravo ! Vous avez trouvé le mot !")
            self._disable_input()
        elif self.current_row >= MAX_TRIES:
            self.status_label.setText("😞 Plus d'essais.")
            self._disable_input()

    def on_submit_guess(self):
        guess = self.guess_input.text().strip()
        if len(guess) == self.word_length:
            self.controller.send_guess(guess)
            self.status_label.setText("")
        else:
            self.status_label.setText(f"Le mot doit faire {self.word_length} lettres.")

    def _disable_input(self):
        self.guess_input.setEnabled(False)
        self.submit_btn.setEnabled(False)

    def set_status(self, message: str, error: bool = False):
        color = "#e74c3c" if error else "#27ae60"
        self.status_label.setStyleSheet(f"font-size: 13px; color: {color};")
        self.status_label.setText(message)
