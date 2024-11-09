import subprocess
import os
from uuid import uuid4

def convert_to_hls(input_file, qualities):
    """Конвертирует видео в HLS, создавая уникальную папку для всех файлов и генерируя их по разрешению."""
    # Генерация уникального идентификатора для папки
    unique_id = uuid4().hex[:8]
    output_dir = f"output_{unique_id}"  # Путь к уникальной папке в корне программы
    os.makedirs(output_dir, exist_ok=True)

    # Словарь разрешений и битрейтов для каждого качества
    quality_map = {
        "2160p": {"resolution": "3840x2160", "bitrate": "30000000"},
        "1440p": {"resolution": "2560x1440", "bitrate": "15000000"},
        "1080p": {"resolution": "1920x1080", "bitrate": "8000000"},
        "720p": {"resolution": "1280x720", "bitrate": "4000000"},
        "480p": {"resolution": "854x480", "bitrate": "2000000"},
        "360p": {"resolution": "640x360", "bitrate": "1000000"},
        "240p": {"resolution": "426x240", "bitrate": "700000"},
        "144p": {"resolution": "256x144", "bitrate": "400000"}
    }

    # Создание мастер-плейлиста
    master_playlist_path = os.path.join(output_dir, "master.m3u8")
    with open(master_playlist_path, "w") as master_playlist:
        master_playlist.write("#EXTM3U\n")

        # Цикл для обработки каждого качества
        for quality in qualities:
            config = quality_map.get(quality)
            if not config:
                print(f"Пропущено качество {quality}: настройки не найдены.")
                continue
            
            resolution = config["resolution"]
            bitrate = config["bitrate"]
            
            # Папка для текущего качества внутри уникальной папки в HLS_video
            quality_folder = os.path.join(output_dir, quality)
            os.makedirs(quality_folder, exist_ok=True)
            
            stream_output = os.path.join(quality_folder, f"{quality}.m3u8")

            # Команда для конвертации с учетом битрейта и разрешения для каждого качества
            command = [
                "ffmpeg", "-i", input_file,
                "-vf", f"scale={resolution}",               # Масштабирование до нужного разрешения
                "-c:a", "aac", "-ar", "48000", "-b:a", "128k",  # Аудиокодек и битрейт
                "-c:v", "h264_nvenc",                       # Использование GPU-кодека для NVIDIA
                "-preset", "slow",                          # Высокое качество кодирования
                "-crf", "18",                               # Параметр Constant Rate Factor для высокого качества
                "-b:v", bitrate,                            # Битрейт для текущего разрешения
                "-maxrate", bitrate,                        # Максимальный битрейт
                "-profile:v", "high",                       # Профиль для совместимости с современными устройствами
                "-g", "48", "-keyint_min", "48",            # Настройки GOP для улучшения ключевых кадров
                "-hls_time", "4", "-hls_playlist_type", "vod",  # Настройки HLS-плейлиста
                "-hls_segment_filename", os.path.join(quality_folder, f"{quality}_%03d.ts"),  # Имя для HLS сегментов
                stream_output
            ]

            # Запуск ffmpeg для выполнения команды
            subprocess.run(command, check=True)

            # Добавление потока в мастер-плейлист
            master_playlist.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={resolution}\n")
            master_playlist.write(f"{quality}/{quality}.m3u8\n")

    print(f"Конвертация завершена. Файлы HLS сохранены в папке: {output_dir}")
    return output_dir  # Возвращаем путь к уникальной папке, например "HLS_video/output_<unique_id>"
