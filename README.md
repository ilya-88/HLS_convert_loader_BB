# HLS Convert Loader BB

**HLS Convert Loader BB** — это приложение для конвертации видео в формат HLS и загрузки файлов на Backblaze B2. Оно поддерживает выбор уровня качества видео и обеспечивает многопоточную загрузку для повышения скорости. Проект создан с использованием PyQt5 для интерфейса.

## Оглавление

- [Особенности](#особенности)
- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
- [Структура проекта](#структура-проекта)
- [Логирование](#логирование)

## Особенности

- Выбор видеофайла и определение его качества.
- Конвертация видео в формат HLS.
- Поддержка выбора уровня качества видео (2160p, 1440p, 1080p, 720p, 480p).
- Многопоточная загрузка конвертированных файлов на Backblaze B2.
- Настраиваемый интерфейс PyQt5 для удобного взаимодействия.

## Требования

- Python 3.x
- Модули: `requests`, `concurrent.futures`, `tenacity`, `PyQt5`
- Утилита `ffmpeg` (для конвертации видео)

## Установка

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/yourusername/HLS_convert_loader_BB.git
    cd HLS_convert_loader_BB
    ```

2. Установите необходимые зависимости:

    ```bash
    pip install -r requirements.txt
    ```

3. Убедитесь, что `ffmpeg` и `ffprobe` установлены и доступны в `PATH`.

## Использование

1. Запустите приложение:

    ```bash
    python main.py
    ```

2. При первом запуске необходимо настроить параметры авторизации для Backblaze:
    - Откройте диалог авторизации и введите данные: имя `bucket`, `application_key_id`, `application_key`, `region`, и `server_name`.
    - Эти данные сохранятся в `auth_data.json` и будут загружены при следующем запуске.

3. Выберите видеофайл, укажите нужное качество и начните конвертацию и загрузку.

4. Логи работы сохраняются в файлы `upload_to_backblaze.log` и `log.txt`.

## Структура проекта

- **`main.py`** — Основной файл для запуска приложения, содержит логику инициализации и интерфейс.
- **`auth_dialog.py`** — Диалог авторизации для ввода и сохранения данных Backblaze.
- **`main_window_interface.py`** — Главное окно приложения с кнопками для выбора видео, настройки качества и запуска конвертации и загрузки.
- **`uploader.py`** — Функции для многопоточной загрузки файлов на Backblaze B2.
- **`video_selector.py`** — Функции для выбора видеофайла и определения его разрешения.
- **`quality_selection.py`** — Интерфейс для выбора уровней качества видео.
- **`hls_converter.py`** — Модуль для конвертации видеофайла в формат HLS.

## Логирование

Все события и ошибки записываются в `log.txt` и `upload_to_backblaze.log` для отслеживания процесса и выявления ошибок.
