# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import logging

import requests
import telegram
import smtplib
import objectpath
from telegram.ext import Updater, Handler, MessageHandler
from telegram.ext import Filters
from telegram.ext import CommandHandler

# API keys
api_file = open('api_key.txt', 'r')
ors_token = api_file.readline()
tg_token = api_file.readline()
api_file.close()

updater = Updater(token=tg_token, use_context=True)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

bot = telegram.Bot(token=tg_token)
dispatcher = updater.dispatcher

location_keyboard = telegram.KeyboardButton(text="Знайти паркінг поруч", request_location=True)
custom_keyboard = [[ location_keyboard ]]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

current_location = [None] * 2
longitude = 0
latitude = 0

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Цей бот допоможе знайти вам найближчий паркінг!")
    bot.send_message(chat_id=update.effective_chat.id,
                     reply_markup=reply_markup, text="Будь ласка, відправте ваші геодані.")


def get_summary(json):
    return json["features"][0]["properties"]["summary"]


def get_location(update, context):
    global longitude
    global latitude
    longitude = update.message.location.longitude
    latitude = update.message.location.latitude
    current_location[0] = longitude
    current_location[1] = latitude
    respond_nearest_parking(update, context)


def respond_nearest_parking(update, context):
    global longitude
    global latitude
    end_longitude = 24.0266211
    end_latitude = 49.8433737
    request = 'https://api.openrouteservice.org/v2/directions/driving-car?api_key=' + ors_token + \
            '&start=' + str(longitude) + ',' + str(latitude) + \
              '&end=' + str(end_longitude) + ',' + str(end_latitude)
    response = requests.get(request)
    if response.status_code == 200:
        summary = get_summary(response.json())
        distance = round(summary["distance"] / 1000, 2)
        duration = round(summary["duration"] / 60)
        print(str(distance) + ' км ' + str(duration) + ' хв')
        update.message.reply_location(longitude=end_longitude, latitude=end_latitude)
        update.message.reply_text(
            text='Найближчий паркінг: ' + str(distance).format() + ' км\n'
                'Орієнтовне прибуття: через ' + str(duration) + ' хв')
    else:
        update.message.reply_text(text='Вибачте, неможливо отримати інформацію про паркінг.')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start_handler = CommandHandler('start', start)
    location_handler = CommandHandler('send_location', get_location)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(MessageHandler(filters=Filters.location, callback=get_location))
    updater.start_polling()
