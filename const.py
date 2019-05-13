import time

with open('bot_token.txt', 'r') as file:
    bot_token = file.readline()

with open('weather_token.txt', 'r') as file:
    weather_token = file.readline()

random_id = time.time()
