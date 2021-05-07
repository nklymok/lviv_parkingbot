# lviv_parkingbot
##### Table of Contents  
- [Українською](#ua)
    - [Про проект](#about-ua)
    - [Як користуватись](#usage-ua)
    - [Скріншоти](#screenshots-ua)
    - [Встановлення (для розробників)](#installation-ua)
        - [Реквізити](#prereq-ua)
- [English](#en)  
    - [About](#about)  
    - [Usage](#usage)  
    - [Screenshots](#screenshots)  
    - [Installation (developers only)](#installation)
        - [Pre-requisites](#prereq)

<a href="ua"></a>
# Українською

<a href="about-ua"></a>
## Про проект
Знаходьте львівські паркінги в Telegram. Швидке та просте рішення всіх проблем із паркуванням. Дізнайтесь:

- Які паркінги є поряд з Вами.
- Наскільки далеко знаходиться найближчий паркінг.
- Скільки часу потрібно добиратись до наближчого паркінгу.
- Скільки паркомісць є на паркінгу.
- Скільки паркомісць для людей з інвалідністю є на паркінгу.
- Де знаходиться другий найближчий паркінг.
<a href="usage-ua"></a>
## Використання:
Це дуже просто:
1) Відкрийте Telegram.
2) Напишіть ботові [@lviv_parkingbot](t.me/lviv_parkingbot).
3) Включіть геолокацію на Вашому пристрої.
4) Відправте Вашу локацію ботові. Як? Просто натисність кнопку внизу чату.
5) Отримайте відповідь! Прикладу на скріншоті внизу.
<a href="screenshots-ua"></a>
## Скріншоти:
![Скріншот 1:](https://snipboard.io/ytxXrm.jpg "Про бота")
![Скріншот 2:](https://snipboard.io/aTOFEM.jpg "Інструкція щодо використання")
![Скріншот 3:](https://i.imgur.com/P5g0COg.png "Бот в дії")
![Скріншот 4:](https://snipboard.io/10Uaef.jpg "Локація паркінгу")
<a href="installation-ua"></a>
## Встановлення (для розробників):
Якщо Ви хочете створити свого бота.
<a href="prereq-ua"></a>
#### Pre-requisites:
- Телеграм-бот і його токен. Створіть бота використовуючи [BotFather-бота](t.me/botfather), і отримайте токен.
- OpenRouteService API ключ. Отримайте його після реєстрації на Їхньому [офіційному веб-сайті](https://openrouteservice.org).
1) Завантажте цей репозиторій.
2) Встановіть всі необхідні залежності на pipenv (`python-telegram-bot, openpyxl, requests, telegram`)
3) В `api_key.txt`: 
    - У перший рядок, введіть Ваш ORS (OpenRouteService) API ключ;
    - У другий рядок, Введіть токен вашого Telegram-бота;
4) Почніть бота.
5) Насолоджуйтесь!

<a href="en"></a>
# English

<a href="about"></a>
## About
Discover Lviv parking lots near You on Telegram. Quick and simple solution for all parking problems. Find out:

- What parking lots are near You.
- How far away the nearest parking lot is.
- How much time it takes to get to the nearest parking lot.
- How many parking spots there are.
- How many inclusive parking spots there are.
- Where the next closest parking lot is.
<a href="usage"></a>
## Usage:
It's really that easy:
1) Go to Telegram.
2) Start the bot [@lviv_parkingbot](t.me/lviv_parkingbot).
3) Turn on geolocation on Your device.
4) Send Your location to the bot. How? Simply press the button in the bottom of the chat.
5) Receive the response! See screenshots below.
<a href="screenshots"></a>
## Screenshots:
![Screenshot 1:](https://snipboard.io/ytxXrm.jpg "Bot About page")
![Screenshot 2:](https://snipboard.io/aTOFEM.jpg "Bot instructions")
![Screenshot 3:](https://i.imgur.com/P5g0COg.png "Bot in action")
![Screenshot 4:](https://snipboard.io/10Uaef.jpg "Telegram location feature in action")
<a href="installation"></a>
## Installation (developers only):
In case You would like to have Your own bot.
<a href="prereq"></a>
#### Pre-requisites:
- Telegram bot and it's token. Create the bot using [BotFather bot](t.me/botfather), and receive the token after creation.
- OpenRouteService API key. Receieve it after signing up on their [official website](https://openrouteservice.org).
1) Download the repository.
2) Install all the needed dependencies for pipenv (`python-telegram-bot, openpyxl, requests, telegram`)
3) In `api_key.txt`: 
    - on the first line, put Your ORS (OpenRouteService) API key;
    - on the second line, put Your Telegram bot token;
4) Start the bot.
5) Enjoy!
