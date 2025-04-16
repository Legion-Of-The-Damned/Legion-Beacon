import requests
import os
import sys
import zipfile
import tempfile
import shutil
import json

CURRENT_VERSION = "0.6"
VERSION_INFO_URL = "https://raw.githubusercontent.com/YourName/YourRepo/main/latest.json"

def get_latest_version_info():
    response = requests.get(VERSION_INFO_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Не удалось получить информацию о последней версии.")

def download_and_extract_zip(url, extract_to):
    zip_path = os.path.join(extract_to, "update.zip")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    os.remove(zip_path)

def check_for_update():
    temp_dir = tempfile.mkdtemp()
    try:
        latest_info = get_latest_version_info()
        latest_version = latest_info["version"]
        download_url = latest_info["url"]

        if latest_version != CURRENT_VERSION:
            print(f"Доступна новая версия: {latest_version}. Текущая: {CURRENT_VERSION}")
            print("Скачивание и распаковка новой версии...")

            download_and_extract_zip(download_url, temp_dir)

            exe_path = None
            for root_dir, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".exe"):
                        exe_path = os.path.join(root_dir, file)
                        break

            if exe_path:
                print(f"Запуск новой версии: {exe_path}")
                os.execv(exe_path, sys.argv)
            else:
                print("Исполняемый файл не найден после распаковки.")
        else:
            print("Установлена последняя версия.")
    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    check_for_update()
