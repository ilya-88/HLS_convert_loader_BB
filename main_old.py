from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QPushButton, QFileDialog, QMessageBox
import subprocess
import json
import sys

def select_video_file():
    """Функция для выбора видеофайла через диалоговое окно."""
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Выберите видеофайл", "", "Video Files (*.mp4 *.mkv *.mov *.avi)", options=options)
    return file_path

def get_video_quality(file_path):
    """Функция для получения разрешения видео с помощью ffprobe."""
    try:
        command = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "json", file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = json.loads(result.stdout)
        
        width = info['streams'][0]['width']
        height = info['streams'][0]['height']
        
        print(f"Разрешение видео: {width}x{height}")
        return width, height
    except Exception as e:
        print("Ошибка при получении качества видео:", e)
        return None

class QualitySelectionWindow(QWidget):
    def __init__(self, max_width, max_height):
        super().__init__()
        self.setWindowTitle("Выбор качества")
        
        self.layout = QVBoxLayout()
        
        # Варианты качества
        self.qualities = {
            "2160p": (3840, 2160),
            "1440p": (2560, 1440),
            "1080p": (1920, 1080),
            "720p": (1280, 720),
            "480p": (854, 480)
        }
        
        # Создаем чекбоксы для каждого качества
        self.checkboxes = {}
        for quality, (width, height) in self.qualities.items():
            checkbox = QCheckBox(quality)
            if width <= max_width and height <= max_height:
                checkbox.setChecked(True)  # Автоматически отмечаем доступные качества
            self.layout.addWidget(checkbox)
            self.checkboxes[quality] = checkbox

        # Кнопка подтверждения
        self.confirm_button = QPushButton("Подтвердить")
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.layout.addWidget(self.confirm_button)
        
        self.setLayout(self.layout)
    
    def confirm_selection(self):
        # Сбор выбранных качеств
        selected_qualities = [quality for quality, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        
        if selected_qualities:
            print("Выбранные качества:", selected_qualities)
            self.close()
        else:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите хотя бы одно качество.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    file_path = select_video_file()
    if file_path:
        print("Выбранный файл:", file_path)
        quality = get_video_quality(file_path)
        if quality:
            max_width, max_height = quality
            window = QualitySelectionWindow(max_width, max_height)
            window.show()
            sys.exit(app.exec_())
        else:
            print("Не удалось определить качество видео.")
    else:
        print("Видео не выбрано.")
