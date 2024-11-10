"""
Этот файл является частью проекта HLS_convert_loader_BB.
Создан совместно пользователем ilya-88 и ChatGPT (OpenAI) для реализации выбора видеофайлов и определения их качества перед конвертацией в HLS.

File purpose: Этот файл содержит функции для выбора видеофайла через интерфейс и для определения разрешения видеофайла.
"""


from PyQt5.QtWidgets import QFileDialog
import subprocess
import json

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
        
        # Извлечение ширины и высоты видео
        width = info['streams'][0]['width']
        height = info['streams'][0]['height']
        
        print(f"Разрешение видео: {width}x{height}")
        return width, height
    except Exception as e:
        print("Ошибка при получении качества видео:", e)
        return None
