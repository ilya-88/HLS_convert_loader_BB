from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QMessageBox

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
        self.selected_qualities = [quality for quality, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        
        if self.selected_qualities:
            print("Выбранные качества:", self.selected_qualities)
            self.close()
        else:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите хотя бы одно качество.")
    
    def get_selected_qualities(self):
        """Возвращает выбранные качества после подтверждения."""
        return self.selected_qualities if hasattr(self, 'selected_qualities') else []
