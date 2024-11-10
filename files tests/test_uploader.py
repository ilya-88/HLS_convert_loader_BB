from uploader import upload_to_backblaze

# Замените на свои данные
output_path = "output/0001"
bucket_name = "dsfgbdrfndr"
application_key_id = "0038e4682478917000000000a"
application_key = "K0038VXpiOU6KYALurwcInRJu/zWLac"
region = "eu-central-003"  # Пример региона

# Запуск загрузки на Backblaze B2
public_url = upload_to_backblaze(output_path, bucket_name, application_key_id, application_key, region)
print("Публичная ссылка на HLS мастер-плейлист:", public_url)
