from PyQt5.QtWidgets import QApplication
import sys
from quality_selection import QualitySelectionWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Пример: тестируем на разрешении 1920x1080
    window = QualitySelectionWindow(1920, 1080)
    window.show()
    app.exec_()
    
    # Получаем выбранные качества
    selected_qualities = window.get_selected_qualities()
    print("Выбранные качества после подтверждения:", selected_qualities)
