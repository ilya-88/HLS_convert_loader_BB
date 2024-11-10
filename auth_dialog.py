import os
import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки авторизации")

        # Поля для авторизации с увеличенной шириной
        self.bucket_name_input = QLineEdit()
        self.application_key_id_input = QLineEdit()
        self.application_key_input = QLineEdit()
        self.region_input = QLineEdit("s3.eu-central-003")
        self.server_name_input = QLineEdit("f003.backblazeb2.com")
        
        # Увеличиваем минимальную ширину полей ввода
        self.bucket_name_input.setMinimumWidth(300)
        self.application_key_id_input.setMinimumWidth(300)
        self.application_key_input.setMinimumWidth(300)
        self.region_input.setMinimumWidth(300)
        self.server_name_input.setMinimumWidth(300)

        # Загрузка данных при открытии диалога
        self.load_auth_data()

        # Используем QFormLayout для улучшенного выравнивания элементов
        layout = QFormLayout()

        # Добавляем метки и поля ввода
        layout.addRow(QLabel("Имя корзины:"), self.bucket_name_input)
        layout.addRow(QLabel("ID ключа:"), self.application_key_id_input)
        layout.addRow(QLabel("Ключ:"), self.application_key_input)
        layout.addRow(QLabel("Регион:"), self.region_input)
        layout.addRow(QLabel("Имя сервера:"), self.server_name_input)

        # Кнопка подтверждения
        self.confirm_button = QPushButton("Подтвердить")
        self.confirm_button.clicked.connect(self.save_and_close)
        layout.addWidget(self.confirm_button)

        # Устанавливаем отступы, чтобы элементы не слипались
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.setLayout(layout)

        # Устанавливаем минимальные размеры для окна
        self.setFixedSize(400, 300)

    def save_and_close(self):
        """Сохраняет данные авторизации в файл и закрывает окно."""
        auth_data = {
            "bucket_name": self.bucket_name_input.text(),
            "application_key_id": self.application_key_id_input.text(),
            "application_key": self.application_key_input.text(),
            "region": self.region_input.text(),
            "server_name": self.server_name_input.text()
        }
        with open("auth_data.json", "w") as file:
            json.dump(auth_data, file)
        self.accept()

    def load_auth_data(self):
        """Загружает данные авторизации из файла, если они существуют."""
        if os.path.exists("auth_data.json"):
            with open("auth_data.json", "r") as file:
                auth_data = json.load(file)
                self.bucket_name_input.setText(auth_data.get("bucket_name", ""))
                self.application_key_id_input.setText(auth_data.get("application_key_id", ""))
                self.application_key_input.setText(auth_data.get("application_key", ""))
                self.region_input.setText(auth_data.get("region", "s3.eu-central-003"))
                self.server_name_input.setText(auth_data.get("server_name", "f003.backblazeb2.com"))

    def get_credentials(self):
        """Возвращает данные авторизации."""
        return {
            "bucket_name": self.bucket_name_input.text(),
            "application_key_id": self.application_key_id_input.text(),
            "application_key": self.application_key_input.text(),
            "region": self.region_input.text(),
            "server_name": self.server_name_input.text()
        }
