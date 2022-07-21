from VK import VK_user
from YaDisk import YandexDisk


if __name__ == '__main__':
    user_vk = VK_user()
    user_name = user_vk.get_user_name()
    albums = user_vk.get_photos()
    user_ya = YandexDisk()
    user_ya.generate_dirs(user_name, albums)
    user_ya.full_upload(albums)



