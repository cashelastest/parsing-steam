import telebot
from telegram.constants import ParseMode
import requests
import psycopg2
from deep_translator import GoogleTranslator
from telebot import types
# Use any translator you like, in this example GoogleTranslator
from slugify import slugify
def strikethrough(text):
    return ''.join(c + '\u0336' for c in text)



api_token = ''
bot = telebot.TeleBot(api_token)


conn = psycopg2.connect(dbname = "Post", user = "postgres", password = "", host = "localhost", port = 5432)

c = conn.cursor()
def counte():
	numbers = 0
	c.execute("""SELECT game_id FROM post """)
	for i in c.fetchall():
		numbers +=1
	print(numbers)

def download_image(name, link):
	img_data = requests.get(link).content
	with open(f'photos/{name}.jpg', 'wb') as handler:
		handler.write(img_data)
	photo = f'photos/{name}.jpg'
	return photo
counte()
@bot.message_handler(commands=['delete'])
def delete(message):
	c.execute("""DELETE FROM post""")
	conn.commit()
@bot.message_handler(commands=['content', 'start'])
def send_game(message):

	c.execute("""SELECT * FROM post WHERE is_posted = 0 ORDER BY players """)
	
	i = 0
	markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1=types.KeyboardButton("контент")
	markup.add(item1)
	for row in c.fetchall():
		i+=1
		if row[6] != 1:
			print(row[7])
			description = GoogleTranslator(source='auto', target='uk').translate(f"{row[2]}")
			img = download_image(row[0], row[5])
			c.execute(""" UPDATE post SET is_posted = %s WHERE game_id = %s""", (1, row[0]))
			price_initial = strikethrough(f"{row[3]} ")
			link = f'https://store.steampowered.com/app/{row[0]}/{slugify(row[1])}/'
			click = f"[Клік]({link})"

			text =f"*{row[1]}*\n\n{description}\n\nЦіна:  {price_initial} => _{row[4]}_ \n\n {click}"
	
			if "&amp;" in text:
				text = text.replace("&amp;", '  ')

			if "&quot;" in text:
				text = text.replace("&quot;", '--')

			bot.send_photo(message.chat.id,photo=open(img, 'rb'), caption=text, parse_mode='Markdown', reply_markup=markup)
			break
	if i==0:
		bot.send_message(message.chat.id, "Все скидки закончились. Попробуйте снова через некоторое время")
		print("no data")
@bot.message_handler(content_types='text')
def message_reply(message):
	if message.text == 'контент':
		send_game(message)
	if message.text =='a':
		for i in range(1,100000):
			print(i)
	if message.text == 'l':
		bot.send_message(message.chat.id, "<a href = 'https://google.com' >Клік</a>",parse_mode = ParseMode.HTML)

bot.polling(none_stop=True)
