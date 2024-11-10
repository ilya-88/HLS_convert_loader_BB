import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import logging
from datetime import datetime
from auth_dialog import AuthDialog  # Импортируем AuthDialog
from hls_converter import convert_to_hls
from uploader import upload_to_backblaze
from video_selector import select_video_file, get_video_quality

# Настройка логирования
logging.basicConfig(filename="log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

AUTH_FILE = "auth_data.json"

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HLS Loader")
        self.setGeometry(300, 300, 600, 400)

        # Основной layout
        layout = QVBoxLayout()

        # Выбор видео
        self.video_path_display = QLineEdit()
        self.video_path_display.setReadOnly(True)
        self.select_video_button = QPushButton("Выбрать видео")
        self.select_video_button.clicked.connect(self.select_video)
        
        # Чекбокс "Авто" и функция для автоматического выбора разрешений
        self.auto_checkbox = QCheckBox("Авто")
        self.auto_checkbox.setChecked(True)  # Установить по умолчанию
        self.auto_checkbox.stateChanged.connect(self.auto_select_qualities)
        
        # Layout выбора видео
        video_layout = QHBoxLayout()
        video_layout.addWidget(QLabel("Выберите видеофайл:"))
        video_layout.addWidget(self.video_path_display)
        video_layout.addWidget(self.select_video_button)
        # Layout для авто и остальных чекбоксов качества
        auto_layout = QHBoxLayout()
        auto_layout.addWidget(self.auto_checkbox)

        # Кнопка для открытия окна авторизации
        self.auth_button = QPushButton("Настройки авторизации")
        self.auth_button.clicked.connect(self.open_auth_dialog)
        
        # Чекбоксы для выбора качества (горизонтальный макет)
        qualities_layout = QHBoxLayout()
        self.quality_checkboxes = {
            "2160p": QCheckBox("2160p"),
            "1440p": QCheckBox("1440p"),
            "1080p": QCheckBox("1080p"),
            "720p": QCheckBox("720p"),
            "480p": QCheckBox("480p"),
            "360p": QCheckBox("360p"),
            "240p": QCheckBox("240p"),
            "144p": QCheckBox("144p")
        }
        for checkbox in self.quality_checkboxes.values():
            auto_layout.addWidget(checkbox)

        layout.addLayout(auto_layout)

        # Кнопка запуска процесса
        self.start_button = QPushButton("Начать")
        self.start_button.clicked.connect(self.start_process)
        
        # Поле для вывода статуса
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        
        # Добавляем элементы в основной layout
        layout.addLayout(video_layout)
        layout.addWidget(self.auth_button)
        layout.addWidget(QLabel("Выберите качество"))
        layout.addLayout(qualities_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(QLabel("Статус выполнения"))
        layout.addWidget(self.status_display)
        
        self.setLayout(layout)
        
        # Загружаем данные авторизации при запуске
        self.load_auth_data()

    def open_auth_dialog(self):
        """Открывает окно авторизации и сохраняет данные после подтверждения."""
        dialog = AuthDialog(self)
        if dialog.exec_():  # Если окно закрыто кнопкой «Подтвердить», сохраняем данные
            self.auth_data = dialog.get_credentials()
            logging.info("Данные авторизации обновлены")

    def load_auth_data(self):
        """Загружает данные авторизации при запуске, если файл существует."""
        if os.path.exists(AUTH_FILE):
            with open(AUTH_FILE, "r") as file:
                self.auth_data = json.load(file)
                logging.info("Данные авторизации загружены")

    def select_video(self):
        """Выбор видеофайла и автоматическое определение доступного качества."""
        file_path = select_video_file()
        if file_path:
            self.video_path_display.setText(file_path)
            quality = get_video_quality(file_path)
            if quality:
                width, height = quality
                quality_map = {
                    "2160p": (3840, 2160),
                    "1440p": (2560, 1440),
                    "1080p": (1920, 1080),
                    "720p": (1280, 720),
                    "480p": (854, 480),
                    "360p": (640, 360),
                    "240p": (426, 240),
                    "144p": (256, 144)
                }
                for q, (w, h) in quality_map.items():
                    self.quality_checkboxes[q].setEnabled(w <= width and h <= height)
                self.auto_select_qualities()

    def auto_select_qualities(self):
        """Автоматически выбирает доступные разрешения, если включен чекбокс 'Авто'."""
        if self.auto_checkbox.isChecked():
            for quality, checkbox in self.quality_checkboxes.items():
                checkbox.setChecked(checkbox.isEnabled())
                
    def start_process(self):
        """Запуск процесса конвертации и загрузки."""
        input_file = self.video_path_display.text()
        selected_qualities = [q for q, cb in self.quality_checkboxes.items() if cb.isChecked()]
        
        # Проверяем авторизацию перед началом
        if hasattr(self, 'auth_data') and input_file and selected_qualities:
            # Запуск конвертации
            self.update_status("Запуск конвертации...")
            output_folder_path = convert_to_hls(input_file, selected_qualities)  # Сохраняем путь к созданной папке
            
            # Запуск загрузки
            self.update_status("Начало загрузки...")
            friendly_url, s3_url = upload_to_backblaze(
                output_folder_path, 
                self.auth_data["bucket_name"], 
                self.auth_data["application_key_id"], 
                self.auth_data["application_key"], 
                self.auth_data["region"],
                self.auth_data["server_name"]
            )
            self.update_status(f"Загрузка завершена.\nДружественная ссылка: {friendly_url}\nS3-совместимая ссылка: {s3_url}")
        else:
            self.update_status("Ошибка: Проверьте данные авторизации, выбор видео и качество.")
    
    def update_status(self, message):
        """Обновление статуса на экране и в лог-файле."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.status_display.append(f"{timestamp} - {message}")
        logging.info(message)


# Для запуска приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
