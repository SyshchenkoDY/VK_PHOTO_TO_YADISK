import time
import requests
from tqdm import tqdm

VK_TOKEN = input('Введите токен ВК: ')
OWNER_ID = input('Введите ID пользователя ВК: ')


class VK_user:
    def __init__(self, token=VK_TOKEN, owner_id=OWNER_ID):
        self.token = token
        self.owner_id = owner_id

    def get_params(self):
        return {
            'owner_id': self.owner_id,
            'count': 200,
            'extended': 1,
            'offset': 0,
            'access_token': self.token,
            'v': '5.131'
        }

    def quantity_photos_user(self):
        url = 'https://api.vk.com/method/photos.getAll'
        response = requests.get(url=url, params=self.get_params())
        quantity_photos = response.json()['response']['count']
        return quantity_photos

    def quantity_iterations_offset(self):
        offset_value = self.get_params()['count']
        quantity_iterations = (self.quantity_photos_user() // offset_value) + 1
        return quantity_iterations

    def get_photos(self):
        albums = {}
        params = self.get_params()
        print(f'--> Загрузка фотографий из ВК!')
        for i in tqdm([i for i in range(self.quantity_iterations_offset())]):
            url = 'https://api.vk.com/method/photos.getAll'
            response = requests.get(url, params=params)
            if response.status_code == 200:
                for photo in response.json()['response']['items']:
                    album_id = str(photo['album_id'])
                    like_name_photo = str(photo['likes']['count'])
                    url_photo = photo['sizes'][-1]['url']
                    size_photo = photo['sizes'][-1]['type']
                    if album_id not in albums:
                        albums[album_id] = {}
                        albums[album_id][like_name_photo] = {
                            'size': size_photo,
                            'url': url_photo
                        }
                    else:
                        if like_name_photo in albums[album_id]:
                            count = ([val.split('(')[0] for val in albums[album_id]]).count(like_name_photo)
                            albums[album_id][f"{like_name_photo}({str(count)})"] = {
                                'size': size_photo,
                                'url': url_photo
                            }
                        else:
                            albums[album_id][f"{like_name_photo}"] = {
                                'size': size_photo,
                                'url': url_photo
                            }
                params['offset'] += 200
                time.sleep(3)
            else:
                print(f'Connection error. Code: {response.status_code}')
        albums = self.rename_albums(albums)
        print(f'--> Количество альбомов у пользователя - {self.get_user_name()}: {len(albums)}')
        print(f'--> Количество фотографий у пользователя - {self.get_user_name()}: {self.quantity_photos_user()}')
        return albums

    def rename_albums(self, albums):
        url_get_albums = 'https://api.vk.com/method/photos.getAlbums'
        params = self.get_params()
        response = requests.get(url=url_get_albums, params=params)
        title_albums = {}
        for album in response.json()['response']['items']:
            title_albums[str(album['id'])] = album['title']
        named_albums = {}
        for key, value in albums.items():
            if str(key) not in title_albums:
                if str(key) == '-6':
                    named_albums['Фотографии на стене'] = value
                elif str(key) == '-7':
                    named_albums['Фотографии на странице'] = value
                else:
                    named_albums[key] = value
            elif str(key) in title_albums:
                named_albums[title_albums[key]] = value
        return named_albums

    def get_user_name(self):
        url_users_get = 'https://api.vk.com/method/users.get'
        res = requests.get(url=url_users_get, params=self.get_params())
        user_name = f'{res.json()["response"][0]["first_name"]} {res.json()["response"][0]["last_name"]}'
        return user_name