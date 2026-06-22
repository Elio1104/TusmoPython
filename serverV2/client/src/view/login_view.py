from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt


class LoginView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        title = QLabel("🎮 TUSMO")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #c0392b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Entrez votre pseudo pour rejoindre :")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #555;")
        layout.addWidget(subtitle)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Pseudo...")
        self.username_input.setFixedSize(220, 36)
        self.username_input.setStyleSheet(
            "border: 2px solid #c0392b; border-radius: 6px; padding: 4px 8px; font-size: 14px;"
        )
        self.username_input.returnPressed.connect(self.on_validate)
        layout.addWidget(self.username_input, alignment=Qt.AlignCenter)

        self.connect_button = QPushButton("Connexion")
        self.connect_button.setFixedSize(120, 40)
        self.connect_button.setStyleSheet(
            "background-color: #c0392b; color: white; font-weight: bold; "
            "border-radius: 6px; font-size: 14px;"
        )
        self.connect_button.clicked.connect(self.on_validate)
        layout.addWidget(self.connect_button, alignment=Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.status_label)

    def on_validate(self):
        username = self.username_input.text().strip()
        if username:
            self.status_label.setText("Connexion en cours...")
            self.connect_button.setEnabled(False)
            self.controller.connect_to_server(username)

    def reset(self):
        self.connect_button.setEnabled(True)
        self.status_label.setText("")
