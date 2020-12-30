# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import logging
from math import radians, cos, sin, asin, sqrt
from pathlib import Path

import openpyxl
import requests
import telegram
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import Updater, MessageHandler

from parkingspot import ParkingSpot

# API keys
api_file = open('api_key.txt', 'r')
ors_token = api_file.readline()
tg_token = api_file.readline()
api_file.close()

# logger / telegram bot config
updater = Updater(token=tg_token, use_context=True)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
bot = telegram.Bot(token=tg_token)
dispatcher = updater.dispatcher

# location keyboard
location_keyboard = telegram.KeyboardButton(text="Знайти паркінг поруч", request_location=True)
custom_keyboard = [[location_keyboard]]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

# excel sheet
xlsx_file = Path('parking.xlsx')
workbook_obj = openpyxl.load_workbook(xlsx_file)
parking_sheet = workbook_obj.active

# parking list
parking_spots = []

# User data
current_location = [None] * 2
longitude = 0
latitude = 0


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers
    return c * r


def get_dist_dur_summary(json):
    return json["features"][0]["properties"]["summary"]


def get_location(update, context):
    global longitude
    global latitude
    longitude = update.message.location.longitude
    latitude = update.message.location.latitude
    current_location[0] = longitude
    current_location[1] = latitude
    respond_nearest_parking(update, context)


def find_distance(parking_spot):
    global longitude
    global latitude

    return haversine(longitude, latitude, parking_spot.longitude, parking_spot.latitude)


def get_nearest_parkingspot():
    closest = parking_spots[0]
    min_distance = find_distance(closest)
    for parking in parking_spots:
        if find_distance(parking) < min_distance:
            closest = parking
            min_distance = find_distance(parking)
    return closest


def respond_nearest_parking(update, context):
    global longitude
    global latitude

    parking_spot = get_nearest_parkingspot()
    request = 'https://api.openrouteservice.org/v2/directions/driving-car?api_key=' + ors_token + \
            '&start=' + str(longitude) + ',' + str(latitude) + \
              '&end=' + str(parking_spot.longitude) + ',' + str(parking_spot.latitude)
    response = requests.get(request)
    if response.status_code == 200:
        summary = get_dist_dur_summary(response.json())
        distance = round(summary["distance"] / 1000, 2)
        duration = round(summary["duration"] / 60)
        print(str(distance) + ' км ' + str(duration) + ' хв')
        update.message.reply_location(latitude=parking_spot.latitude, longitude=parking_spot.longitude)
        update.message.reply_text(
            text='🚗 Найближчий паркінг: ' + parking_spot.address + '\n\n'
                '📏 Відстань: ' + str(distance).format() + ' км\n\n'
                '⌛ Орієнтовне прибуття: через ' + str(duration) + ' хв')
    else:
        update.message.reply_text(text='Вибачте, неможливо отримати інформацію про паркінг.')
        print(response.json())


def load_parking_data():
    for i, row in enumerate(parking_sheet.iter_rows(values_only=True)):
        # row[8] = longitude,latitude | row[10] == address
        if i == 0 or row[1] != 'загального користування':
            continue
        address = str(row[10])
        lat_lon = str(row[8]).split(',', 2)
        parking_spots.append(ParkingSpot(address, float(lat_lon[0]), float(lat_lon[1])))


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Цей бот допоможе знайти вам найближчий паркінг!")
    bot.send_message(chat_id=update.effective_chat.id,
                     reply_markup=reply_markup, text="Будь ласка, відправте ваші геодані.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_parking_data()
    start_handler = CommandHandler('start', start)
    location_handler = CommandHandler('send_location', get_location)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(MessageHandler(filters=Filters.location, callback=get_location))
    updater.start_polling()
