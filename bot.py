import json

import requests
import vk_api
from vk_api.longpoll import VkEventType

from const import *


def iterate_random_id():
    """
    Iterate over unique ids for random_id field for every message request

    :return: next random id
    """
    global random_id
    random_id += 1
    return random_id


def test_message(event):
    """
    Check if user's message satisfies coded patterns

    :param event: event with user's message
    :return: None
    """

    # Greeting
    if "прив" in event.text.lower():
        vk.messages.send(peer_id=event.user_id,
                         message="Приветик! <3",
                         random_id=iterate_random_id())
        vk.messages.send(peer_id=event.user_id,
                         message=
                         '''Вот что я умею:
                         "Покажи погоду в городе <город>" - покажу погоду в указанном городе
                         "Покажи погоду в моём городе" - покажу погоду в городе, который указан на твоей страничке''',
                         random_id=iterate_random_id())
        return
    # city choose
    if event.text.find('Покажи погоду в городе') == 0:
        vk.messages.send(peer_id=event.user_id,
                         message="Секундочку",
                         random_id=iterate_random_id())
        handle_weather_request(event.user_id, event.text[len('Покажи погоду в городе '):])
        return
    # hometown
    # TODO what will happen if current city is not stated?
    if event.text == 'Покажи погоду в моём городе':
        vk.messages.send(peer_id=event.user_id, message="Секундочку", random_id=iterate_random_id())
        handle_weather_request(event.user_id,
                               vk.users.get(user_ids=[event.user_id],
                                            fields=['city'])[0]['city']['title'])
        return
    # thankfulness
    if "пасиб" in event.text.lower():
        vk.messages.send(peer_id=event.user_id,
                         message="Не за что! <3",
                         random_id=iterate_random_id())
        return
    # bragging about dissability to send stickers
    if 'attach1_type' in event.attachments and event.attachments['attach1_type'] == 'sticker':
        vk.messages.send(peer_id=event.user_id,
                         message="Если бы ботам можно было отправлять платные стикеры,"
                                 " я бы только ими и общалась, но увы...",
                         random_id=iterate_random_id())
        return
    # if message does not satisfy any pattern
    vk.messages.send(peer_id=event.user_id,
                     message="Сложно",
                     random_id=iterate_random_id())


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
                                 random_id=iterate_random_id())
                test_message(event)


def handle_weather_request(user_id, city_name):
    """
    Handle requiring weather from openweathermap.org API

    :param user_id: who should get weather report
    :param city_name: where to search for weather forecast
    :return: None
    """
    response = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(city_name, weather_token))
    weather = json.loads(response.text)
    if weather["cod"] != 200:
        vk.messages.send(peer_id=user_id,
                         message="Нету такого города. Если это заграничный город, попробуй написать на английском",
                         random_id=iterate_random_id())
        return
    # TODO do nice images with pillow instead of boring text
    message = 'Так-с, вот что я нашла: сейчас температура {}°C, ветер {} м/с,' \
              ' и вообще погоду можно описать примерно как "{}"'.format(
        int(weather['main']['temp'] - 273.15), weather['wind']['speed'], weather['weather'][0]['description'])
    vk.messages.send(peer_id=user_id,
                     message=message,
                     random_id=iterate_random_id())
    vk.messages.send(peer_id=user_id,
                     message="Вооот",
                     random_id=iterate_random_id())


vk_session = vk_api.VkApi(token=bot_token)
vk = vk_session.get_api()
listen()
