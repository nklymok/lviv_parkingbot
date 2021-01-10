import logging
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import time
import os

import openpyxl
import requests
import telegram
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import Updater, MessageHandler

from parkingspot import ParkingSpot

PORT = int(os.environ.get('PORT', 5000))

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
btn_location_text = "Знайти паркінг поруч"
location_keyboard = telegram.KeyboardButton(text=btn_location_text, request_location=True)
custom_keyboard = [[location_keyboard]]
find_parking_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

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

# Timeout dictionary
user_calltime = {}
timeout = 15


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
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def get_dist_dur_summary(json):
    return json["features"][0]["properties"]["summary"]


def on_timeout(call_time, current_time):
    global timeout
    if call_time is not None and float(current_time) - float(call_time) < float(timeout):
        return True
    return False


def send_on_timeout_message(update, context, time_to_wait):
    update.message.reply_text("Отримати найближчу парковку можна через " + str(int(time_to_wait)) + " секунд!")


def process_location(update, context):
    global longitude
    global latitude
    user_chat_id = update.message.chat_id
    current_time = time.time()
    if on_timeout(user_calltime.get(user_chat_id), current_time):
        send_on_timeout_message(update, context, current_time - user_calltime.get(user_chat_id))
        return
    else:
        user_calltime[user_chat_id] = current_time
        longitude = update.message.location.longitude
        latitude = update.message.location.latitude
        current_location[0] = longitude
        current_location[1] = latitude
        respond_nearest_parking(update, context)


def find_distance(parking_spot):
    global longitude
    global latitude

    return haversine(longitude, latitude, parking_spot.longitude, parking_spot.latitude)


def sort_parkingspots():
    global longitude
    global latitude

    parking_spots.sort(key=find_distance)


def send_parking_spot(update, parking_spot, summary):
    distance = round(summary["distance"] / 1000, 2)
    duration = round(summary["duration"] / 60)
    update.message.reply_location(latitude=parking_spot.latitude, longitude=parking_spot.longitude)
    update.message.reply_text(
        text=
        '🚗 Найближчий паркінг: ' + parking_spot.address + '\n\n'
        '📏 Відстань: ' + str(distance).format() + ' км\n\n'
        '⌛ Орієнтовне прибуття: через ' + str(duration) + ' хв\n\n'
        '🤏 К-ть паркувальних місць: ' + str(parking_spot.parking_places) + '\n\n'
        'ℹ️ К-ть місць для людей з інвалідністю: ' + str(parking_spot.parking_places_dis)
    )


# TODO checked parking lots up to 102
def respond_nearest_parking(update, context):
    global longitude
    global latitude

    sort_parkingspots()
    parking_spot = parking_spots[0]
    request = 'https://api.openrouteservice.org/v2/directions/driving-car?api_key=' + ors_token + \
              '&start=' + str(longitude) + ',' + str(latitude) + \
              '&end=' + str(parking_spot.longitude) + ',' + str(parking_spot.latitude)
    response = requests.get(request)
    if response.status_code == 200:
        send_parking_spot(update, parking_spot, get_dist_dur_summary(response.json()))
    else:
        update.message.reply_text(text='Вибачте, неможливо отримати інформацію про паркінг.')
        print("error: \n" + response.json())


def load_parking_data():
    for i, row in enumerate(parking_sheet.iter_rows(values_only=True)):
        # row[6] = parking places | row[7] = parking places for people with disabilities
        # row[8] = longitude,latitude | row[10] = address
        if i == 0 or row[1] != 'загального користування':
            continue
        address = str(row[10])
        lat_lon = str(row[8]).split(',', 2)
        parking_places = int(row[6])
        parking_places_dis = int(row[7])
        parking_spots.append(ParkingSpot(address, float(lat_lon[0]), float(lat_lon[1]),
                                         parking_places, parking_places_dis))


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=
                                                                "Привіт!\n"
                                                                "Цей бот допоможе вам знайти найближчий паркінг загального користування! 😉\n")
    bot.send_message(chat_id=update.effective_chat.id,
                     reply_markup=find_parking_markup, text=
                                                        "🔍 Будь ласка, відправте ваші геодані, або локацію, поряд з якою хочете знайти паркінг\n"
                                                        "Для цього:\n"
                                                        "а) натисніть на кнопку \"" + btn_location_text + "\",\n"
                                                        "б) або натисніть на 📎 (вкладення) в чаті зліва від поля вводу"
                                                        " та відправте локацію.")


def main():
    load_parking_data()
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(MessageHandler(filters=Filters.location, callback=process_location))
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=tg_token)
    updater.bot.setWebhook('https://parkingbot-lviv.herokuapp.com/' + tg_token)
    updater.idle()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
