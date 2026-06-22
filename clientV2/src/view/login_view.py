from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt


class LoginView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Entrez votre pseudo :")
        layout.addWidget(self.label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Pseudo...")
        self.username_input.setFixedSize(200, 30)
        layout.addWidget(self.username_input)

        self.connect_button = QPushButton("Valider")
        self.connect_button.setFixedSize(100, 40)
        self.connect_button.setStyleSheet("background-color: white;")
        layout.addWidget(self.connect_button, alignment=Qt.AlignCenter)

        # Connexion du clic au contrôleur
        self.connect_button.clicked.connect(self.on_validate)

    def on_validate(self):
        username = self.username_input.text()
        if username:
            self.controller.connect_to_server(username)