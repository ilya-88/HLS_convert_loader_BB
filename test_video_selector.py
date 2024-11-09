from PyQt5.QtWidgets import QApplication
import sys
from video_selector import select_video_file, get_video_quality

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    file_path = select_video_file()
    if file_path:
        print("Выбранный файл:", file_path)
        quality = get_video_quality(file_path)
        if quality:
            print(f"Качество видео: {quality[0]}x{quality[1]}")
        else:
            print("Не удалось определить качество видео.")
    else:
        print("Видео не выбрано.")
