import logging

# haversine, timer stuff
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import time
import os

# Telegram, http, spreadsheet management
import openpyxl
import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import Filters
from telegram.ext import Updater, MessageHandler

# Custom classes
from parkingspot import ParkingSpot
from geocode import Geocode

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

instructions = "Для цього:\n" \
                "а) натисніть на кнопку \"" + btn_location_text + "\",\n" \
                "б) або натисніть на 📎 (вкладення) в чаті збоку від поля вводу та відправте локацію."

# excel sheet
xlsx_file = Path('parking.xlsx')
workbook_obj = openpyxl.load_workbook(xlsx_file)
parking_sheet = workbook_obj.active

# parking list
parking_lots = []

# Userid to location map, userid to parking index map, current userid (used to share id while sorting parking lots)
user_id_location = {}
user_id_parking_index = {}
parking_index_limit = 5
current_userid = -1

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


def time_format(time):
    if time < 60:
        return str(time) + " хв."
    hours = time / 60
    minutes = time % 60
    if minutes == 0:
        return str(int(hours)) + " год. "
    return str(int(hours)) + " год. " + str(minutes) + " хв."


def get_dist_dur_summary(json):
    return json["features"][0]["properties"]["summary"]


def on_timeout(call_time, current_time):
    global timeout
    if call_time is not None and float(current_time) - float(call_time) < float(timeout):
        return True
    return False


def send_on_timeout_message(message, context, time_to_wait):
    message.reply_text("Отримати найближчий паркінг можна через " + str(int(time_to_wait)) + " секунд!")


# Get user id, check for timeout -> save calltime, geocode in map, rest parking index in map, prepare parking
def process_location(update, context):
    user_chat_id = update.message.chat_id
    current_time = time.time()
    if on_timeout(user_calltime.get(user_chat_id), current_time):
        send_on_timeout_message(update.message, context, timeout - (current_time - user_calltime.get(user_chat_id)))
        return
    else:
        user_calltime[user_chat_id] = current_time
        user_id_location[update.message.chat_id] = Geocode(
            update.message.location.longitude,
            update.message.location.latitude)
        user_id_parking_index[update.message.chat_id] = 0
        prepare_parking_lots(update, context)


def find_distance(parking_lot):
    global current_userid

    user_geocode = user_id_location[current_userid]
    return haversine(user_geocode.longitude, user_geocode.latitude,
                     parking_lot.longitude, parking_lot.latitude)


def sort_parkinglots():
    parking_lots.sort(key=find_distance)


def send_parking_lot(message, parking_lot, distance, duration):
    message.reply_location(latitude=parking_lot.latitude, longitude=parking_lot.longitude)
    keyboard = [
        [InlineKeyboardButton("Ще один паркінг поруч", callback_data=message.chat_id)],
    ]
    reply_next_parking_markup = InlineKeyboardMarkup(keyboard)
    message.reply_text(
        text=
        '🚗 Найближчий паркінг: ' + parking_lot.address + '\n\n'
        '📏 Відстань: ' + str(distance).format() + ' км\n\n'
        '⌛ Орієнтовне прибуття: через ' + str(duration) + '\n\n'
        '🤏 К-ть паркувальних місць: ' + str(parking_lot.parking_places) + '\n\n'
        'ℹ️ К-ть місць для людей з інвалідністю: ' + str(parking_lot.parking_places_dis),
        reply_markup=reply_next_parking_markup
    )


def summary_get_distance(summary):
    return round(summary["distance"] / 1000, 2)


def summary_get_duration(summary):
    return time_format(round(summary["duration"] / 60))


def request_summary(user_geocode, parking_lot):
    request = 'https://api.openrouteservice.org/v2/directions/driving-car?api_key=' + ors_token + \
              '&start=' + str(user_geocode.longitude) + ',' + str(user_geocode.latitude) + \
              '&end=' + str(parking_lot.longitude) + ',' + str(parking_lot.latitude)
    print('start: ' + (str(user_geocode.longitude) + ',' + str(user_geocode.latitude)) + '|end: '
          + (str(user_geocode.longitude) + ',' + str(user_geocode.latitude)))
    response = requests.get(request)
    print(response.text)
    if response.status_code == 200:
        return get_dist_dur_summary(response.json())
    else:
        print("error: \n" + response.json())


# Get callback, check timeout, check for parking index limit, send parking
def next_parking_lot(callback_update, context):
    query = callback_update.callback_query
    query.answer()
    user_id = query.message.chat_id
    current_time = time.time()
    if on_timeout(user_calltime.get(user_id), current_time):
        send_on_timeout_message(query.message, context, timeout - (current_time - user_calltime.get(user_id)))
        return
    user_geocode = user_id_location[user_id]
    parking_index = user_id_parking_index[user_id]
    if parking_index > parking_index_limit:
        query.message.reply_text(text="Ви вже знайшли " + str(parking_index_limit) +
                                      " найближчих паркінгів 😢\n\n"
                                      "Проте ви можете спробувати знайти паркінги поряд з вашою новою локацією!\n"
                                      + instructions)
        return
    user_id_parking_index[user_id] = user_id_parking_index[user_id] + 1
    parking_lot = parking_lots[user_id_parking_index[user_id]]
    summary = request_summary(user_geocode, parking_lot)
    if summary is not None:
        send_parking_lot(query.message, parking_lot, summary_get_distance(summary), summary_get_duration(summary))
        query.edit_message_text(text=query.message.text + "\n\n🆕 Новий паркінг відправлено!")
        return
    else:
        query.message.reply_text(text='Вибачте, неможливо отримати інформацію про паркінг.')
        return


# TODO checked parking lots up to 370, 0 to go
# receive user geocode from map
# sort parkings, get user parking index, request summary,
# send message with distance and duration from summary to user
def prepare_parking_lots(update, context):
    global user_id_parking_index
    global current_userid

    user_id = update.message.chat_id
    user_geocode = user_id_location[user_id]
    current_userid = user_id
    sort_parkinglots()
    current_userid = -1
    parking_lot = parking_lots[user_id_parking_index[user_id]]
    summary = request_summary(user_geocode, parking_lot)
    if summary is not None:
        print("user: " + str(user_geocode.latitude) + ", " + str(user_geocode.longitude) + " | \n"
              "result: " + str(parking_lot.latitude) + ", " + str(parking_lot.longitude))
        send_parking_lot(update.message, parking_lot, summary_get_distance(summary), summary_get_duration(summary))
    else:
        update.message.reply_text(text='Вибачте, неможливо отримати інформацію про паркінг.')


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
        parking_lots.append(ParkingSpot(address, float(lat_lon[0]), float(lat_lon[1]),
                                        parking_places, parking_places_dis))


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=
                             "Привіт!\n"
                             "Цей бот допоможе вам знайти найближчий паркінг загального користування! 😉\n")
    bot.send_message(chat_id=update.message.chat_id,
                     reply_markup=find_parking_markup,
                     text=
                     "🔍 Будь ласка, відправте ваші геодані, або локацію, поряд з якою хочете знайти паркінг\n"
                     + instructions)


def main():
    load_parking_data()
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(MessageHandler(filters=Filters.location, callback=process_location))
    dispatcher.add_handler(CallbackQueryHandler(next_parking_lot))
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=tg_token)
    updater.bot.setWebhook('https://parkingbot-lviv.herokuapp.com/' + tg_token)
    updater.idle()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
