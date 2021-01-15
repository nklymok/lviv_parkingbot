# lviv_parkingbot
##### Table of Contents  
- [About](#about)  
- [Usage](#usage)  
- [Screenshots](#screenshots)  
- [Installation](#installation)
    - [Pre-requisites](#prereq)

<a href="about"></a>
## About
Discover Lviv parking lots near you on Telegram. Quick and simple solution for all parking problems.
Find out:
- What parkings are near you.
- How far away is the nearest parking spot.
- How much time it takes to get to the nearest parking spot.
- How many parking spots are there.
- How many inclusive parking spots are there.
<a href="usage"></a>
## Usage:
It's really that easy:
1) Go to Telegram.
2) Start the bot [@lviv_parkingbot](t.me/lviv_parkingbot).
3) Turn on geolocation on your device.
4) Send your location to the bot. How? Simply press the button in the bottom of the chat.
5) Receive the response! See screenshots below.
<a href="screenshots"></a>
## Screenshots:
![Screenshot 1:](https://snipboard.io/ytxXrm.jpg "Bot About page")
![Screenshot 2:](https://snipboard.io/aTOFEM.jpg "Bot instructions")
![Screenshot 3:](https://snipboard.io/DcAgru.jpg "Bot in action")
![Screenshot 4:](https://snipboard.io/10Uaef.jpg "Telegram location feature in action")
<a href="installation"></a>
## Installation:
In case you would like to have your own bot.
<a href="prereq"></a>
#### Pre-requisites:
- Telegram bot and it's token. Create the bot using [BotFather bot](t.me/botfather), and receive the token after creation.
- OpenRouteService API key. Receieve it after signing up on their [official website](https://openrouteservice.org).
1) Download the repository.
2) Install all the needed dependencies for pipenv (`python-telegram-bot, openpyxl, requests, telegram`)
3) In `api_key.txt`: 
    - on the first line, put your ORS (OpenRouteService) API key;
    - on the second line, put your Telegram bot token;
4) Start the bot.
5) Enjoy!
