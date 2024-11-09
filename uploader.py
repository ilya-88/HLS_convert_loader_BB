import requests
import os
from pathlib import Path
import concurrent.futures

def upload_to_backblaze(unique_folder_path, bucket_name, application_key_id, application_key, region):
    """Загружает уникальную папку на Backblaze B2 с многопоточностью и сохранением структуры."""
    # Авторизация на Backblaze B2
    auth_url = "https://api.backblazeb2.com/b2api/v2/b2_authorize_account"
    auth_response = requests.get(auth_url, auth=(application_key_id, application_key))
    auth_data = auth_response.json()

    if "code" in auth_data:
        raise ValueError(f"Ошибка авторизации: {auth_data.get('message', 'Неизвестная ошибка')}")

    api_url = auth_data["apiUrl"]
    auth_token = auth_data["authorizationToken"]

    # Получение bucketId
    list_buckets_url = f"{api_url}/b2api/v2/b2_list_buckets"
    headers = {"Authorization": auth_token}
    params = {"accountId": auth_data["accountId"]}
    response = requests.post(list_buckets_url, headers=headers, json=params)
    buckets = response.json()

    bucket_id = next((b["bucketId"] for b in buckets["buckets"] if b["bucketName"] == bucket_name), None)
    if not bucket_id:
        raise ValueError(f"Bucket с именем {bucket_name} не найден.")

    # Получение всех файлов для загрузки
    files_to_upload = list(Path(unique_folder_path).glob("**/*"))
    if not files_to_upload:
        raise ValueError(f"Нет файлов для загрузки в директории {unique_folder_path}.")

    # Функция для загрузки файла
    def upload_file(file):
        # Получаем новый токен и URL для каждой загрузки файла
        upload_url_response = requests.post(
            f"{api_url}/b2api/v2/b2_get_upload_url",
            headers={"Authorization": auth_token},
            json={"bucketId": bucket_id}
        )
        upload_url_data = upload_url_response.json()
        if "code" in upload_url_data:
            raise ValueError(f"Ошибка получения URL для загрузки: {upload_url_data['message']}")
        
        upload_url = upload_url_data["uploadUrl"]
        upload_auth_token = upload_url_data["authorizationToken"]

        with open(file, "rb") as f:
            file_data = f.read()
        file_name = f"HLS_video/{file.relative_to(Path(unique_folder_path).parent)}".replace("\\", "/")
        print(f"Загрузка файла: {file_name}")

        # Отправка файла
        upload_response = requests.post(
            upload_url,
            headers={
                "Authorization": upload_auth_token,
                "X-Bz-File-Name": file_name,
                "Content-Type": "b2/x-auto",
                "X-Bz-Content-Sha1": "do_not_verify",
            },
            data=file_data
        )
        upload_result = upload_response.json()
        if "fileId" not in upload_result:
            raise ValueError(f"Ошибка при загрузке файла {file_name}: {upload_result.get('message', 'Неизвестная ошибка')}")
        else:
            print(f"Файл {file_name} успешно загружен.")

    # Многопоточная загрузка файлов с обновлением токена для каждого файла
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(upload_file, file) for file in files_to_upload if file.is_file()]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Ошибка при загрузке файла: {e}")

    # Ссылки на мастер-плейлист
    friendly_url = f"https://f003.backblazeb2.com/file/{bucket_name}/HLS_video/{Path(unique_folder_path).name}/master.m3u8"
    s3_url = f"https://{bucket_name}.{region}.backblazeb2.com/HLS_video/{Path(unique_folder_path).name}/master.m3u8"
    
    return friendly_url, s3_url
