import telebot
from decouple import config
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_keyboard = InlineKeyboardMarkup(row_width=4)
for i in range(4):
    btn1 = InlineKeyboardButton(str(i*4+1), callback_data=(i*4+1))
    btn2 = InlineKeyboardButton(str(i*4+2), callback_data=(i*4+2))
    btn3 = InlineKeyboardButton(str(i*4+3), callback_data=(i*4+3))
    btn4 = InlineKeyboardButton(str(i*4+4), callback_data=(i*4+4))
    inline_keyboard.add(btn1, btn2, btn3, btn4)

bot = telebot.TeleBot(config('TOKEN'))

BASE_URL = 'https://www.eldorado.ru/c/smartfony/'

titles = {}
images = {}
prices = {}

def parsing(url):
    global titles, images, prices
    headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    main = soup.find('div', {'id': 'listing-container'}).find('ul', class_='GridInner_list___8u79').find_all('li', class_='ListingProductCardList_productCardListingWrapper__3-o9i')[:16]
    for i, product in enumerate(main, 1):
        titles[i] = product.find('div', class_='ListingProductCardList_productCardListingDescription__q4iOE').find('a', class_='ListingProductCardList_productCardListingLink__1JIMi').text
        images[i] = product.find('img', class_='ListingProductCardImage_listingProductCardImage__2fGmx').get('src')
        prices[i] = product.find('span', class_='PriceBlock_buyBoxPrice__3QGyj PriceBlock_buyBoxPriceStyled__29J_G').text.replace('\xa0', ' ')
    name_title = '' 
    for i in range(1, len(titles)+1):
        name_title += f'{i}: {titles[i]}\n' 
    return name_title, images, prices

@bot.message_handler(commands=['start',])
def welcome(message):
    name_title, images, prices = parsing(BASE_URL)
    bot.send_message(message.chat.id, name_title, reply_markup=inline_keyboard)



@bot.callback_query_handler(func=lambda c:True)
def callback_inline(c):
    item = int(c.data)
    bot.send_message(c.message.chat.id, titles[item])
    bot.send_photo(c.message.chat.id, images[item])
    bot.send_message(c.message.chat.id, prices[item])


bot.polling(none_stop=True)
