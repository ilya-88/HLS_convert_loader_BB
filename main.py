import os
import json
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon  # Import QIcon for setting icons
from video_selector import select_video_file, get_video_quality
from quality_selection import QualitySelectionWindow
from hls_converter import convert_to_hls
from uploader import upload_to_backblaze
from main_window_interface import MainWindow

def check_and_create_auth_file():
    """Проверяет наличие файла auth_data.json и создает его с шаблоном, если отсутствует."""
    auth_file = "auth_data.json"
    if not os.path.exists(auth_file):
        # Шаблонные данные для файла auth_data.json
        auth_data_template = {
            "bucket_name": "your_name_bucket",
            "application_key_id": "BACKBLAZE_KEY",
            "application_key": "BACKBLAZE_SECRET",
            "region": "region_your_bucket",
            "server_name": "f003.backblazeb2.com"  # Добавлено название сервера
        }
        
        # Создаем файл с шаблонными данными
        with open(auth_file, "w") as file:
            json.dump(auth_data_template, file, indent=4)

def load_auth_data():
    """Загружает данные авторизации из auth_data.json."""
    with open("auth_data.json", "r") as file:
        return json.load(file)

def validate_auth_data(auth_data):
    """Проверяет, заполнены ли данные авторизации."""
    return all(auth_data.get(key) and "your" not in auth_data[key].lower() 
               for key in ["bucket_name", "application_key_id", "application_key", "region", "server_name"])

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу в собранном приложении или в исходной директории """
    try:
        # Для собранного приложения с помощью PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Для исходного кода, если не собрано в .exe
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class AppMain(QApplication):
    def __init__(self, auth_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Устанавливаем рабочую директорию как директорию с исполняемым файлом .exe
        if hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)
        else:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

        try:
            self.setWindowIcon(QIcon(resource_path('app_icon.png')))  # Иконка для панели задач
            self.auth_data = auth_data
            self.main_window = MainWindow()
            self.main_window.setWindowIcon(QIcon(resource_path('app_icon_32.png')))  # Иконка для заголовка окна
            self.main_window.show()
        except Exception as e:
            self.handle_error(e)

    def handle_error(self, error):
        """Метод для обработки ошибок."""
        print(f"Произошла ошибка: {error}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Ошибка")
        msg.setText(f"Произошла ошибка:\n{error}")
        msg.exec_()


        # Загрузка на Backblaze и получение двух ссылок
        try:
            bucket_name = self.auth_data["bucket_name"]
            application_key_id = self.auth_data["application_key_id"]
            application_key = self.auth_data["application_key"]
            region = self.auth_data["region"]
            server_name = self.auth_data["server_name"]  # Загружаем название сервера из конфигурации

            file_server_url, s3_server_url = upload_to_backblaze(
                output_dir, 
                bucket_name, 
                application_key_id, 
                application_key, 
                region, 
                server_name
            )

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Ошибка загрузки")
            msg.setText(f"Ошибка при загрузке на Backblaze: {str(e)}")
            msg.exec_()
            return

        # Вывод ссылок в окне уведомления
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Ссылки на мастер-плейлист")
        msg.setText(f"Ссылка на файл-сервер:\n{file_server_url}\n\nСсылка на S3-сервер:\n{s3_server_url}")
        msg.exec_()

if __name__ == "__main__":
    # Выполняем проверку и создание auth_data.json при первом запуске
    check_and_create_auth_file()

    # Загружаем данные авторизации
    try:
        auth_data = load_auth_data()
    except Exception as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Ошибка загрузки данных авторизации")
        msg.setText(f"Не удалось загрузить файл auth_data.json: {str(e)}")
        msg.exec_()
        sys.exit(1)
    
    # Запуск приложения
    app = AppMain(auth_data, sys.argv)
    sys.exit(app.exec_())
