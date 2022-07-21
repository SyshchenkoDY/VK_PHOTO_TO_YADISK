import time
import requests
from tqdm import tqdm

YA_TOKEN = input('Введите токен ЯндексДиска: ')


class YandexDisk:
    def __init__(self, token=YA_TOKEN):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def generate_dirs(self, user_name: str, albums: dict):
        self.user_name = user_name
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = self.get_headers()
        print(f'--> Создание папки пользователя "{self.user_name}" на ЯндексДиске!')
        response = requests.put(f'{url}?path=Фотографии {self.user_name}', headers=headers)
        time.sleep(1)
        if response.status_code == 409 or response.status_code == 201:
            print('--> Папка успешно создана!')
            time.sleep(1)
            print(f'--> Создание альбомов в папке пользователя!')
            for k, v in albums.items():
                response = requests.put(f'{url}?path=Фотографии {self.user_name}/{str(k)}', headers=headers)
                if requests.get(f'{url}?path=Фотографии {self.user_name}', headers=headers).status_code == 200:
                    print(f'--> Каталог альбома "{str(k)}" успешно создан!')
                else:
                    print(f'--> Ошибка создания каталога альбома "{str(k)}"!')
                time.sleep(1)
        else:
            print(f'Connection error. Code: {response.status_code}')

    def get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': disk_file_path, 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file(self, disk_file_path, filename):
        response_href = self.get_upload_link(disk_file_path=disk_file_path)
        href = response_href.get('href', '')
        res = requests.put(href, data=filename)


    def full_upload(self, albums):
        for album, photos in albums.items():
            name_album = album
            headers = self.get_headers()
            time.sleep(1)
            print(f'\n--> Загрузка альбома "{name_album}" на ЯндексДиск:')
            upload_album = {}
            for name, data_photo in photos.items():
                file_name = name
                link = data_photo['url']
                upload_album[file_name] = link
            len_album = [k for k in upload_album.keys()]
            time.sleep(1)
            for i in tqdm(len_album):
                url = requests.get(str(upload_album[i]))
                self.upload_file(disk_file_path=f'Фотографии {self.user_name}/{name_album}/{str(i)}.jpg',
                                    filename=url.content)
                if requests.get(f'https://cloud-api.yandex.net/v1/disk/resources?path=Фотографии {self.user_name}/{name_album}/{str(i)}.jpg', headers=headers).status_code == 200:
                    with open('log.txt', 'a', encoding='utf-8') as f:
                        f.write(f'Фотография: "{i}"\n'
                                f'Альбом "{name_album}"\n'
                                f'Статус: "Добавлена"\n\n')
                else:
                    with open('log.txt', 'a', encoding='utf-8') as f:
                        f.write(f'Фотография: "{i}"\n'
                                f'Альбом "{name_album}"\n'
                                f'Статус: "Ошибка загрузки!"\n\n')
                    print(f'\nФотография "{str(i)}" из альбома "{name_album}" не загружена!')
            time.sleep(1)
        print('--> Все фотографии загружены на ЯндексДиск! Отчет в файле "log.txt"')