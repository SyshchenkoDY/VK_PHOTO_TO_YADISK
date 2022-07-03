import requests
from pprint import pprint
import time
from tqdm import tqdm
import pickle


VK_TOKEN = input('Введите токен ВК: ')
OWNER_ID = input('Введите ID пользователя ВК: ')
YA_DISK_TOKEN = input('Введите токен ЯндексДиска: ')


class VK:
    def __init__(self, token=VK_TOKEN, owner_id=OWNER_ID):
        self.albums = None
        self.token = token
        self.owner_id = owner_id

    def get_params(self):
        return {
            'owner_id': self.owner_id,
            'count': 200,
            'extended': 1,
            'access_token': self.token,
            'v': '5.131'
        }

    def count_iterations(self):
        url_get_photos = 'https://api.vk.com/method/photos.getAll'
        params_count_photos = self.get_params()
        res_count_photos = requests.get(url=url_get_photos, params=params_count_photos)
        count_photos = res_count_photos.json()['response']['count']
        offset_value = params_count_photos['count']
        iterations = (count_photos // offset_value) + 1
        return iterations

    def get_photos(self):
        albums = {}
        count_photos = 0
        offset = 0
        print('Загрузка фотографий из ВК')
        for i in tqdm([i for i in range(self.count_iterations())]):
            res = requests.get(f'https://api.vk.com/method/photos.getAll?owner_id={self.owner_id}&offset={offset}&count=200&extended=1&access_token={self.token}&v=5.131')
            for photo in res.json()['response']['items']:
                count_photos += 1
                album_id = str(photo['album_id'])
                like_name_photo = str(photo['likes']['count'])
                url_photo = photo['sizes'][-1]['url']
                size_photo = photo['sizes'][-1]['type']
                if album_id not in albums:
                    albums[album_id] = {}
                    albums[album_id][like_name_photo] = [size_photo, url_photo]
                else:
                    if like_name_photo in albums[album_id]:
                        count = ([val.split('_')[0] for val in albums[album_id]]).count(like_name_photo)
                        albums[album_id][f"{like_name_photo}_{str(count)}"] = [size_photo, url_photo]
                    else:
                        albums[album_id][f"{like_name_photo}"] = [size_photo, url_photo]
            offset += 200
            time.sleep(3)
        albums = self.rename_albums(albums)
        print(f'Количество альбомов у пользователя - {self.get_user_name()}: {len(albums)}')
        print(f'Количество фотографий у пользователя - {self.get_user_name()}: {count_photos}')
        return albums

    def generate_json_file(self, albums):
        self.albums = albums
        self.result_json_file = []
        for album, photos in albums.items():
            for photo in photos.items():
                album_name = album
                file_name = photo[0]
                size = photo[1][0]
                self.result_json_file.append({
                    'album_name': f'"{album_name}"',
                    'file_name': f'"{file_name}.jpg"',
                    'size': f'"{size}"'
                })
        with open('json_file', 'wb') as file:
            pickle.dump(self.result_json_file, file)
        print('Файл json создан!')
        return self.result_json_file

    def rename_albums(self, albums):
        url_get_albums = 'https://api.vk.com/method/photos.getAlbums'
        params = self.get_params()
        res = requests.get(url=url_get_albums, params=params)
        albums_info = res.json()
        name_albums = {}
        for album in albums_info['response']['items']:
            name_albums[str(album['id'])] = album['title']
        new_albums = {}
        for key, value in albums.items():
            if str(key) not in name_albums:
                if str(key) == '-6':
                    new_albums['Фотографии на стене'] = value
                elif str(key) == '-7':
                    new_albums['Фотографии на странице'] = value
                else:
                    new_albums[key] = value
            if str(key) in name_albums:
                new_albums[name_albums[key]] = value
        return new_albums

    def get_user_name(self):
        url_users_get = 'https://api.vk.com/method/users.get'
        params = {
            'user_ids': self.owner_id,
            'access_token': self.token,
            'v': '5.131'
        }
        res = requests.get(url=url_users_get, params=params)
        user_name = f'{res.json()["response"][0]["first_name"]} {res.json()["response"][0]["last_name"]}'
        return user_name


class YandexDisk:
    def __init__(self, token=YA_DISK_TOKEN):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def generate_dirs(self, user_name: str):
        self.user_name = user_name
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = self.get_headers()
        res = requests.put(f'{url}?path=Фотографии {self.user_name}', headers=headers)
        for k, v in albums.items():
            res = requests.put(f'{url}?path=Фотографии {self.user_name}/{str(k)}', headers=headers)

    def get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': disk_file_path, 'overwrite': 'true'}
        res = requests.get(upload_url, headers=headers, params=params)
        return res.json()

    def upload_file(self, disk_file_path, filename):
        response_href = self.get_upload_link(disk_file_path=disk_file_path)
        href = response_href.get('href', '')
        res = requests.put(href, data=filename)

    def full_upload(self, albums):
        for album, photos in albums.items():
            name_album = album
            time.sleep(1)
            print(f'\nЗагрузка альбома "{name_album}" на ЯндексДиск:')
            upload_album = {}
            for photo in photos.items():
                file_name = photo[0]
                link = photo[1][1]
                upload_album[file_name] = link
            len_album = [k for k in upload_album.keys()]
            time.sleep(1)
            for i in tqdm(len_album):
                url = requests.get(str(upload_album[i]))
                user_ya.upload_file(disk_file_path=f'Фотографии {user_name}/{name_album}/{str(i)}.jpg',
                                    filename=url.content)
            time.sleep(1)
        print('Все фотографии загружены на ЯндексДиск')


if __name__ == '__main__':
    user_vk = VK()
    user_name = user_vk.get_user_name()
    albums = user_vk.get_photos()

    json_file = user_vk.generate_json_file(albums)

    user_ya = YandexDisk(YA_DISK_TOKEN)
    user_ya.generate_dirs(user_name)
    user_ya.full_upload(albums)


