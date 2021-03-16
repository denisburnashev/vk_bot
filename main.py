import requests
import vk_api
import time
from datetime import date
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

with open('VKtoken.txt', 'r') as file_object:
    vktoken = file_object.read().strip()

with open('group_token.txt', 'r') as file_object:
    token = file_object.read().strip()

people_ids = []
people_photo_url = []
searching_params = {}


class Bot:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.token = token
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version
        }

    def user_sex(self, user_id):
        time.sleep(1)

        user_sex_url = self.url + 'users.get'
        user_sex_params = {
            'user_ids': user_id,
            'fields': 'sex'
        }
        res = requests.get(user_sex_url, params={**self.params, **user_sex_params})
        res = res.json()
        sex = res['response'][0]
        if sex['sex'] is None:
            pass
        else:
            sex = res['response'][0]['sex']
            if sex == 1:
                sex = 2
                return sex
            elif sex == 2:
                sex = 1
                return sex
            else:
                sex = 0
                return sex

    def user_city_id(self, user_id):
        time.sleep(1)

        user_city_id_url = self.url + 'users.get'
        user_city_id_params = {
            'user_ids': user_id,
            'fields': 'city'
        }
        res = requests.get(user_city_id_url, params={**self.params, **user_city_id_params})
        res = res.json()['response'][0]
        if res.get('city') is None:
            pass
        else:
            city_id = res['city']['id']
            return city_id

    def database_get_cities_id(self, city_name):

        user_city_name_id_url = self.url + 'database.getCities'
        user_city_name_id_params = {
            'country_id': 1,
            'need_all': 0
        }
        res = requests.get(user_city_name_id_url, params={**self.params, **user_city_name_id_params})
        res = res.json()
        city_names = res['response']['items']
        for cities in city_names:
            if cities['title'] == city_name:
                return cities['id']

    def user_bdate(self, user_id):
        time.sleep(1)

        user_bdate_url = self.url + 'users.get'
        user_bdate_params = {
            'user_ids': user_id,
            'fields': 'bdate'
        }
        res = requests.get(user_bdate_url, params={**self.params, **user_bdate_params})
        res = res.json()['response'][0]
        if res.get('bdate') is None:
            pass
        else:
            bdate = res['bdate']
            age = bdate[5:]
            today = str(date.today())
            today_year = today[:4]
            your_age = int(today_year) - int(age)
            return your_age

    def user_relation(self, user_id):

        user_relation_url = self.url + 'users.get'
        user_relation_params = {
            'user_ids': user_id,
            'fields': 'relation'
        }
        res = requests.get(user_relation_url, params={**self.params, **user_relation_params})
        res = res.json()
        relation_status = res['response'][0]['relation']
        return relation_status

    def users_searching_optimal(self, sex, city_id, age_from, age_to):

        users_searching_url = self.url + 'users.search'
        users_searching_params = {
            'count': 10,
            'city': city_id,
            'sex': sex,
            'status': 6,
            'age_from': age_from - 2,
            'age_to': age_to + 2
        }
        res = requests.get(users_searching_url, params={**self.params, **users_searching_params})
        res = res.json()
        users_info = res['response']['items']
        for users_url in users_info:
            people_ids.append(users_url['id'])

    def user_searching_your_settings(self, sex, city_id, age_from, age_to):

        user_searching_your_settings_url = self.url + 'users.search'
        user_searching_your_settings_params = {
            'count': 10,
            'city': city_id,
            'sex': sex,
            'status': 6,
            'age_from': age_from,
            'age_to': age_to
        }
        res = requests.get(user_searching_your_settings_url, params={
            **self.params,
            **user_searching_your_settings_params
        })
        res = res.json()
        users_info = res['response']['items']
        for users_url in users_info:
            people_ids.append(users_url['id'])

    def get_photos(self, user_id):

        top_photo = {}

        get_photos_url = self.url + 'photos.get'
        get_photos_params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1
        }
        res = requests.get(get_photos_url, params={**self.params, **get_photos_params})
        res = res.json()
        photo_info = res['response']['items']
        for photo in photo_info:
            top_photo[photo['sizes'][-1]['url']] = photo['likes']['count']
        inverse = [(meaning, social) for social, meaning in top_photo.items()]
        sorted_top_photos = sorted(inverse, reverse=True)
        top = sorted_top_photos[0:3]
        for photos in top:
            people_photo_url.append(photos[1])

    def user_closed_open(self, user_id):

        user_closed_open_url = self.url + 'users.get'
        user_closed_open_params = {
            'user_ids': user_id
        }
        res = requests.get(user_closed_open_url, params={**self.params, **user_closed_open_params})
        res = res.json()
        return res['response'][0]['is_closed']


bot_vk = Bot(vktoken, '5.126')

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            messages = vk.method('messages.getConversations', {'filter': 'unanswered'})
            text = messages['items'][0]['last_message']['text']
            if request == 'привет':
                write_msg(event.user_id, f'Привет это бот - vkinder по поиску людей.\n'
                                         f'Для кого ты хочешь найти подходящих людей?\n'
                                         f'если ты хочешь найти для себя просто напиши - для себя,\n '
                                         f'а если ты хочешь найти для друга введи - для друга и '
                                         f'через пробел укажи его id')
            elif request == 'для себя':
                searching_params['user_id'] = event.user_id
                write_msg(event.user_id, f'Отлично, ты хочешь найти новых знакомых для себя,'
                                         f'я могу предложить два варианта поиска:\n'
                                         f'если интересует быстрый поиск просто введи - быстрый поиск '
                                         f'и в ответ я пришлю тебе ссылку на аккаунт и топ 3 фото профиля\n'
                                         f'если же интересует детальный поиск просто введи - детальный поиск '
                                         f'и в ответ я пришлю тебе ссылку на аккаунт и топ 3 фото профиля')
            elif request == 'для друга':
                write_msg(event.user_id, f'Отлично просто напиши мне id его аккаунта.')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            searching_params['user_id'] = request
                            write_msg(event.user_id, f'если интересует быстрый поиск просто введи - быстрый поиск '
                                                     f'и в ответ я пришлю тебе ссылку на аккаунт и топ 3 фото профиля\n'
                                                     f'если же интересует детальный поиск просто введи - '
                                                     f'детальный поиск и в ответ я пришлю тебе ссылку '
                                                     f'на аккаунт и топ 3 фото профиля')
                            break
            elif request == 'быстрый поиск':
                if (bot_vk.user_sex(searching_params['user_id']) is None) or \
                        (bot_vk.user_city_id(searching_params['user_id']) is None) or \
                        (bot_vk.user_bdate(searching_params['user_id']) is None):
                    write_msg(event.user_id, f'Часть информации отсутствует, рекомендую использовать детальный поиск.')
                else:
                    people_ids.clear()
                    bot_vk.users_searching_optimal(bot_vk.user_sex(searching_params['user_id']),
                                                   bot_vk.user_city_id(searching_params['user_id']),
                                                   bot_vk.user_bdate(searching_params['user_id']),
                                                   bot_vk.user_bdate(searching_params['user_id']))
                    for people in people_ids:
                        people_photo_url.clear()
                        if bot_vk.user_closed_open(people) is False:
                            bot_vk.get_photos(people)
                            write_msg(event.user_id, f'https://vk.com/id{str(people)}')
                            for photo in people_photo_url:
                                write_msg(event.user_id, f'{photo}')
                        elif bot_vk.user_closed_open(people) is True:
                            write_msg(event.user_id, f'https://vk.com/id{str(people)}')
                            write_msg(event.user_id, f'к сожелению это закрытый профиль '
                                                     f'и я не могу отправить тебе его или ее фото.')
            elif request == 'детальный поиск':
                write_msg(event.user_id, f'Отлично, давай тогда определися с несколькими параметрами.\n'
                                         f'Для начала давай определимся какого пола ты хочешь найти людей.\n'
                                         f'Мужского\n'
                                         f'Женского\n'
                                         f'Не имеет значения')
            elif request == 'Мужского':
                searching_params['sex'] = 2
                write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            searching_params['city_id'] = bot_vk.database_get_cities_id(request)
                            if searching_params['city_id'] is None:
                                write_msg(event.user_id, f'Не знаю такого города')
                            else:
                                write_msg(event.user_id, f'{bot_vk.database_get_cities_id(request)}, красивый город, '
                                                         f'осталось лишь с возрастным диапозоном поиска.\n'
                                                         f'Для начала укажи минимальны возраст '
                                                         f'с которого надо начать поиск.')
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW:
                                    if event.to_me:
                                        request = event.text
                                        searching_params['age_from'] = request
                                        write_msg(event.user_id, f'ну и на полследок укажи максимальный возраст.')
                                        for event in longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                if event.to_me:
                                                    request = event.text
                                                    searching_params['age_to'] = request
                                                    people_ids.clear()
                                                    bot_vk.user_searching_your_settings(searching_params['sex'],
                                                                                        searching_params['city_id'],
                                                                                        searching_params['age_from'],
                                                                                        searching_params['age_to'])
                                                    for people in people_ids:
                                                        people_photo_url.clear()
                                                        if bot_vk.user_closed_open(people) is False:
                                                            bot_vk.get_photos(people)
                                                            write_msg(event.user_id, f'https://vk.com/id{str(people)}')
                                                            for photo in people_photo_url:
                                                                write_msg(event.user_id, f'{photo}')
                                                        elif bot_vk.user_closed_open(people) is True:
                                                            write_msg(event.user_id, f'https://vk.com/id{str(people)}')
                                                            write_msg(event.user_id,
                                                                      f'к сожелению это закрытый профиль '
                                                                      f'и я не могу отправить тебе его или ее фото.')
                                                    break

                                        break
                            break
            elif request == 'Женского':
                searching_params['sex'] = 1
                write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            searching_params['city_id'] = bot_vk.database_get_cities_id(request)
                            if searching_params['city_id'] is None:
                                write_msg(event.user_id, f'Не знаю такого города')
                            else:
                                write_msg(event.user_id, f'{bot_vk.database_get_cities_id(request)}, красивый город, '
                                                         f'осталось лишь с возрастным диапозоном поиска.\n'
                                                         f'Для начала укажи минимальны возраст '
                                                         f'с которого надо начать поиск.')
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW:
                                    if event.to_me:
                                        request = event.text
                                        searching_params['age_from'] = request
                                        write_msg(event.user_id, f'ну и на полследок укажи максимальный возраст.')
                                        for event in longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                if event.to_me:
                                                    request = event.text
                                                    searching_params['age_to'] = request
                                                    people_ids.clear()
                                                    bot_vk.user_searching_your_settings(searching_params['sex'],
                                                                                        searching_params['city_id'],
                                                                                        searching_params['age_from'],
                                                                                        searching_params['age_to'])
                                                    for people in people_ids:
                                                        people_photo_url.clear()
                                                        if bot_vk.user_closed_open(people) is False:
                                                            bot_vk.get_photos(people)
                                                            write_msg(event.user_id, f'https://vk.com/id{str(people)}')
                                                            for photo in people_photo_url:
                                                                write_msg(event.user_id, f'{photo}')
                                                        elif bot_vk.user_closed_open(people) is True:
                                                            write_msg(event.user_id, f'https://vk.com/id{str(people)}')
                                                            write_msg(event.user_id,
                                                                      f'к сожелению это закрытый профиль '
                                                                      f'и я не могу отправить тебе его или ее фото.')
                                                    break

                                        break
                            break
            elif request == 'Не имеет значения':
                searching_params['sex'] = 0
                write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            searching_params['city_id'] = bot_vk.database_get_cities_id(request)
                            if searching_params['city_id'] is None:
                                write_msg(event.user_id, f'Не знаю такого города')
                            else:
                                write_msg(event.user_id, f'{bot_vk.database_get_cities_id(request)}, красивый город, '
                                                         f'осталось лишь с возрастным диапозоном поиска.\n'
                                                         f'Для начала укажи минимальны возраст '
                                                         f'с которого надо начать поиск.')
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW:
                                    if event.to_me:
                                        request = event.text
                                        searching_params['age_from'] = request
                                        write_msg(event.user_id, f'ну и на полследок укажи максимальный возраст.')
                                        for event in longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                if event.to_me:
                                                    request = event.text
                                                    searching_params['age_to'] = request
                                                    people_ids.clear()
                                                    bot_vk.user_searching_your_settings(searching_params['sex'],
                                                                                        searching_params['city_id'],
                                                                                        searching_params['age_from'],
                                                                                        searching_params['age_to'])
                                                    for people in people_ids:
                                                        people_photo_url.clear()
                                                        if bot_vk.user_closed_open(people) is False:
                                                            bot_vk.get_photos(people)
                                                            write_msg(event.user_id, f'https://vk.com/id{str(people)}')
                                                            for photo in people_photo_url:
                                                                write_msg(event.user_id, f'{photo}')
                                                        elif bot_vk.user_closed_open(people) is True:
                                                            write_msg(event.user_id, f'https://vk.com/id{str(people)}')
                                                            write_msg(event.user_id,
                                                                      f'к сожелению это закрытый профиль '
                                                                      f'и я не могу отправить тебе его или ее фото.')
                                                    break

                                        break
                            break
