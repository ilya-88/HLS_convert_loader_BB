import json
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from video_selector import select_video_file, get_video_quality
from quality_selection import QualitySelectionWindow
from hls_converter import convert_to_hls
from uploader import upload_to_backblaze
from main_window_interface import MainWindow

def load_auth_data():
    """Загружает данные авторизации из auth_data.json."""
    with open("auth_data.json", "r") as file:
        return json.load(file)

class AppMain(QApplication):
    def __init__(self, auth_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_data = auth_data
        self.main_window = MainWindow()
        self.main_window.show()

    def start_conversion_and_upload(self, input_file, qualities):
        """Запускает процесс конвертации и загрузки, затем отображает ссылки."""
        # Конвертация видео в HLS и создание уникальной папки
        output_dir = convert_to_hls(input_file, qualities)

        # Загрузка на Backblaze и получение двух ссылок
        bucket_name = self.auth_data["bucket_name"]
        application_key_id = self.auth_data["application_key_id"]
        application_key = self.auth_data["application_key"]
        file_server_url, s3_server_url = upload_to_backblaze(
            output_dir, bucket_name, application_key_id, application_key, 
            file_server=self.auth_data["file_server"], region=self.auth_data["region"]
        )

        # Вывод ссылок в окне уведомления
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Ссылки на мастер-плейлист")
        msg.setText(f"Ссылка на файл-сервер:\n{file_server_url}\n\nСсылка на S3-сервер:\n{s3_server_url}")
        msg.exec_()

if __name__ == "__main__":
    # Загружаем данные авторизации
    auth_data = load_auth_data()
    
    # Запуск приложения
    app = AppMain(auth_data, sys.argv)
    sys.exit(app.exec_())
