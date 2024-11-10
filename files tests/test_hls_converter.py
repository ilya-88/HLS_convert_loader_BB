from hls_converter import convert_to_hls

# Укажите путь к видео и выберите тестовые качества
input_file = "C:/0001.mp4"  # Замените на ваш тестовый файл
qualities = ["1080p", "720p"]  # Выберите разрешения для теста

# Запуск конвертации
convert_to_hls(input_file, qualities)
