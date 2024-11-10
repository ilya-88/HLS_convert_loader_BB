import requests
import os
from pathlib import Path
import concurrent.futures
import logging
from tenacity import retry, wait_fixed, stop_after_attempt

# Настроим логирование ошибок
logging.basicConfig(filename='upload_to_backblaze.log', level=logging.INFO)

def upload_to_backblaze(output_dir, bucket_name, application_key_id, application_key, region, server_name):
    """Загружает файлы на Backblaze B2 с использованием многопоточности для увеличения скорости загрузки."""
    
    # Авторизация на Backblaze B2
    auth_url = "https://api.backblazeb2.com/b2api/v2/b2_authorize_account"
    auth_response = requests.get(auth_url, auth=(application_key_id, application_key))
    
    if auth_response.status_code != 200:
        raise ValueError(f"Ошибка авторизации: {auth_response.status_code} - {auth_response.text}")
       
    auth_data = auth_response.json()
    api_url = auth_data["apiUrl"]
    if not api_url:
        raise KeyError("Ответ авторизации не содержит ключ 'apiUrl'. Проверьте учетные данные.")
    auth_token = auth_data["authorizationToken"]

    # Получаем bucketId по имени bucketName
    list_buckets_url = f"{api_url}/b2api/v2/b2_list_buckets"
    headers = {"Authorization": auth_token}
    params = {"accountId": auth_data["accountId"]}
    response = requests.post(list_buckets_url, headers=headers, json=params)
    buckets = response.json()
    bucket_id = next((b["bucketId"] for b in buckets["buckets"] if b["bucketName"] == bucket_name), None)
    if not bucket_id:
        raise ValueError(f"Bucket с именем {bucket_name} не найден.")

    # Загрузка файлов из уникальной папки с многопоточностью
    files_to_upload = list(Path(output_dir).glob("**/*"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(upload_file, file, bucket_id, auth_token, api_url, output_dir)
            for file in files_to_upload if file.is_file()
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Ошибка при загрузке файла: {e}")
                print(f"Ошибка при загрузке файла: {e}")

    # Возвращаем обе ссылки на мастер-плейлист
    friendly_url = f"https://f003.backblazeb2.com/file/{bucket_name}/HLS_video/{output_dir}/master.m3u8"
    s3_url = f"https://{bucket_name}.s3.{region}.backblazeb2.com/HLS_video/{output_dir}/master.m3u8"
    return friendly_url, s3_url

@retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
def upload_file(file_path, bucket_id, auth_token, api_url, output_dir):
    """Загружает один файл напрямую."""
    
    try:
        upload_url_response = requests.post(
            f"{api_url}/b2api/v2/b2_get_upload_url",
            headers={"Authorization": auth_token},
            json={"bucketId": bucket_id}
        )
        
        upload_url_data = upload_url_response.json()
        upload_url = upload_url_data["uploadUrl"]
        upload_auth_token = upload_url_data["authorizationToken"]

        # Загружаем файл
        with open(file_path, "rb") as f:
            file_data = f.read()

        # Формируем правильное имя файла в бакете
        file_name = f"HLS_video/{output_dir}/{file_path.relative_to(output_dir)}".replace("\\", "/")
        
        response = requests.post(upload_url, headers={
            "Authorization": upload_auth_token,
            "X-Bz-File-Name": file_name,
            "Content-Type": "b2/x-auto",
            "X-Bz-Content-Sha1": "do_not_verify"
        }, data=file_data)
        
        if response.status_code != 200:
            raise ValueError(f"Ошибка при загрузке файла {file_name}: {response.json().get('message', 'Неизвестная ошибка')}")
        else:
            print(f"Файл {file_name} успешно загружен.")
            logging.info(f"Файл {file_name} успешно загружен.")

    except Exception as e:
        logging.error(f"Ошибка при загрузке файла {file_path}: {e}")
        raise e

