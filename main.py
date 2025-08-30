import telebot
from telebot import types
from sqlite3 import *

bot = telebot.TeleBot(YOUR_BOT_TOKEN_HERE)
#Creating connection with new database and creating table if not exists
conn = connect('list.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
task TEXT NOT NULL
)
''')
conn.commit()
conn.close()

@bot.message_handler(commands=['start', 'help'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='/new')
    btn2 = types.KeyboardButton(text='/add')
    btn3 = types.KeyboardButton(text='/list')
    btn4 = types.KeyboardButton(text='/delete')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, '''Hello! In this bot you can do your own ToDo 
lists and save it!
To create list use command /new\nTo add new task use command /add\nTo see your lists use command /list
To delete list use command /delete
    ''', reply_markup=markup)

@bot.message_handler(commands=['new'])
def add(message):
    bot.send_message(message.chat.id, 'Please enter name for new list!')
    bot.register_next_step_handler(message, process_name)

def process_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'And now enter first task!')
    bot.register_next_step_handler(message, process_task)

def process_task(message):
    task = message.text
    conn = connect('list.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, task) VALUES (?, ?)', (name, task))

    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, 'Your list has been created!')

@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, 'Enter the name of the list to which you want to add the task')
    bot.register_next_step_handler(message, check_list)

def check_list(message):
    global list_name
    list_name = message.text
    conn = connect('list.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE name = ?', (list_name,))
    exists = cursor.fetchone()
    conn.close()

    if not exists:
        bot.send_message(message.chat.id, 'List does not exist!')
        bot.register_next_step_handler(message, add)
        return

    bot.send_message(message.chat.id, 'Please enter the task')
    bot.register_next_step_handler(message, new_task)

def new_task(message):
    task = message.text
    conn = connect('list.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, task) VALUES (?, ?)', (list_name, task))
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, f'List {list_name} has been updated!')

@bot.message_handler(commands=['list'])
def ask_list_name(message):
    bot.send_message(message.chat.id, 'Please enter list name to see tasks')
    bot.register_next_step_handler(message, show_list)

def show_list(message):
    name_list = message.text

    conn = connect('list.db')
    cursor = conn.cursor()
    cursor.execute('SELECT task FROM users WHERE name = ?', (name_list,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        bot.send_message(message.chat.id, 'List does not exist or no tasks has been added!')
    else:
        text = f'List {name_list}\n'
        for i, row in enumerate(rows, 1):
            text += f'{i}. {row[0]}\n'
        bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['delete'])
def delete_list(message):
    msg = bot.send_message(message.chat.id, 'Enter list name to delete')
    bot.register_next_step_handler(msg, do_delete_list)

def do_delete_list(message):
    list_name = message.text.strip()

    conn = connect('list.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE name = ?", (list_name,))
    rows = cursor.fetchall()

    if not rows:
        bot.send_message(message.chat.id, f'List {list_name} has not found!')
    else:
        cursor.execute("DELETE FROM users WHERE name = ?", (list_name,))
        conn.commit()
        bot.send_message(message.chat.id, f'List {list_name} has been deleted!')

    conn.close()


bot.polling(none_stop=True)