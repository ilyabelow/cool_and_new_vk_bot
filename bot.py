import json
import time

import requests
import vk_api
from vk_api.longpoll import VkEventType


class State:
    def __init__(self):
        with open('bot_token.txt', 'r') as file:
            self.bot_token = file.readline()
        with open('weather_token.txt', 'r') as file:
            self.weather_token = file.readline()
        self.random_id = int(time.time())

    def iterate(self):
        """
        Iterate over unique ids for random_id field for every message request

        :return: next random id
        """
        self.random_id += 1
        return self.random_id


def test_message(event):
    """
    Check if user's message satisfies coded patterns

    :param event: event with user's message
    :return: None
    """
    # Common mistakes from users are not using capital letter and not using ё properly
    text = event.text.lower().replace('ё', 'е')
    # Greeting
    if "прив" in text:
        vk.messages.send(peer_id=event.user_id,
                         message="Приветик! <3",
                         random_id=state.iterate())
        vk.messages.send(peer_id=event.user_id,
                         message=
                         '''Вот что я умею:
                         "Покажи погоду в городе <город>" - покажу погоду в указанном городе
                         "Покажи погоду в моём городе" - покажу погоду в городе, который указан на твоей страничке''',
                         random_id=state.iterate())
        return
    # city choose
    if 'покажи погоду в городе' in text:
        vk.messages.send(peer_id=event.user_id,
                         message="Секундочку",
                         random_id=state.iterate())
        handle_weather_request(event.user_id, text[len('Покажи погоду в городе '):])
        return
    # hometown
    if 'покажи погоду в моем городе' in text:
        vk.messages.send(peer_id=event.user_id, message="Секундочку", random_id=state.iterate())
        user_with_city = vk.users.get(user_ids=[event.user_id], fields=['city'])[0]
        if 'city' in user_with_city.keys():
            handle_weather_request(event.user_id, user_with_city['city']['title'])
        else:
            vk.messages.send(peer_id=event.user_id, message="У тебя на страничке не указан текущий город, "
                                                            "а как определить твоё текущее местоположение по-другому"
                                                            " я не знаю :(", random_id=state.iterate())

        return
    # thankfulness
    if "пасиб" in text:
        vk.messages.send(peer_id=event.user_id,
                         message="Не за что! <3",
                         random_id=state.iterate())
        return
    # bragging about dissability to send stickers
    if 'attach1_type' in event.attachments and event.attachments['attach1_type'] == 'sticker':
        vk.messages.send(peer_id=event.user_id,
                         message="Если бы ботам можно было отправлять платные стикеры,"
                                 " я бы только ими и общалась, но увы...",
                         random_id=state.iterate())
        return
    # if message does not satisfy any pattern
    vk.messages.send(peer_id=event.user_id,
                     message="Сложно",
                     random_id=state.iterate())


def listen():
    """
    Listen for incoming messages

    :return: None
    """
    longpoll = vk_api.longpoll.VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if not event.from_me:
                test_message(event)
        if event.type == VkEventType.MESSAGE_EDIT:
            if not event.from_me:
                vk.messages.send(peer_id=event.user_id,
                                 message="Уууу, редактируешь >:(",
                                 random_id=state.iterate())
                test_message(event)


def handle_weather_request(user_id, city_name):
    """
    Handle requiring weather from openweathermap.org API

    :param user_id: who should get weather report
    :param city_name: where to search for weather forecast
    :return: None
    """
    response = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(city_name, state.weather_token))
    weather = json.loads(response.text)
    if weather["cod"] != 200:
        vk.messages.send(peer_id=user_id,
                         message="Нету такого города. Если это заграничный город, попробуй написать на английском",
                         random_id=state.iterate())
        return
    # TODO do nice images with pillow instead of boring text
    message = 'Так-с, вот что я нашла: сейчас температура {}°C, ветер {} м/с,' \
              ' и вообще погоду можно описать примерно как "{}"'.format(
        int(weather['main']['temp'] - 273.15), weather['wind']['speed'], weather['weather'][0]['description'])
    vk.messages.send(peer_id=user_id,
                     message=message,
                     random_id=state.iterate())
    vk.messages.send(peer_id=user_id,
                     message="Вооот",
                     random_id=state.iterate())


state = State()
vk_session = vk_api.VkApi(token=state.bot_token)
vk = vk_session.get_api()
listen()
