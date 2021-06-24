import os
import sqlite3
from collections import defaultdict
from contextlib import contextmanager

import telebot
from dotenv import load_dotenv
from telebot import types


@contextmanager
def db_connect(db_name):

    try:
        db_connection = sqlite3.connect(db_name)
        cursor = db_connection.cursor()
        yield cursor

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if db_connection:
            print(
                "Всего строк, измененных после подключения к базе данных: ",
                db_connection.total_changes,
            )
            db_connection.close()
            print("Соединение с SQLite закрыто")


if __name__ == "__main__":

    # with db_connect('database.db') as db:
    #     sqlite_create_table_query = '''CREATE TABLE songs123 (
    #                                 id INTEGER PRIMARY KEY,
    #                                 user TEXT NOT NULL UNIQUE,
    #                                 name TEXT NOT NULL UNIQUE,
    #                                 chords TEXT NOT NULL,
    #                                 strumming TEXT NOT NULL,
    #                                 lyrics TEXT NOT NULL);'''
    #     db.execute(sqlite_create_table_query)

    project_folder = os.path.expanduser("~/PycharmProjects/SongsBot")
    load_dotenv(os.path.join(project_folder, ".env"))

    bot = telebot.TeleBot(os.getenv("TOKEN"))

    START, OPTIONS, ADD_TITLE, FIND_TITLE, CHORDS, STRUMMING, LYRICS = range(7)
    USER_STATE = defaultdict(lambda: START)
    CURRENT_SONG = defaultdict(str)

    SONGS = defaultdict(lambda: {})

    def get_song(user_id, title):
        return SONGS[user_id][title]

    def update_song(username, title, key, value):
        SONGS[username][title][key] = value

    def get_state(message):
        return USER_STATE[message.chat.id]

    def update_state(message, state):
        USER_STATE[message.chat.id] = state

    @bot.message_handler(commands=["start"])
    @bot.message_handler(func=lambda message: get_state(message) == START)
    def handle_message(message):
        keyboard = types.ReplyKeyboardMarkup(True)
        add_song_button = types.KeyboardButton("Добавить песню")
        find_song_button = types.KeyboardButton("Найти песню")
        keyboard.row(add_song_button, find_song_button)
        bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=keyboard)
        update_state(message, OPTIONS)

    @bot.message_handler(func=lambda message: get_state(message) == OPTIONS)
    def handle_option(message):
        text = message.text
        if text == "Добавить песню":
            update_state(message, ADD_TITLE)
        elif text == "Найти песню":
            update_state(message, FIND_TITLE)
        bot.send_message(message.chat.id, "Введите автора и навание через дефис")

    @bot.message_handler(func=lambda message: get_state(message) == ADD_TITLE)
    def handle_add_title(message):
        song_title = message.text
        CURRENT_SONG[message.from_user.username] = song_title
        SONGS[message.from_user.username][song_title] = defaultdict()
        update_state(message, CHORDS)
        bot.send_message(message.chat.id, "Введите последовательность аккордов")

    @bot.message_handler(func=lambda message: get_state(message) == FIND_TITLE)
    def handle_find_title(message):
        try:
            song_info = get_song(message.from_user.username, message.text)
            song_info_message = (
                f"Название:\n{message.text}\n\nАккорды:\n{song_info['chords']}\n\n"
                f"Бой:\n{song_info['strumming']}\n\nТекст:\n{song_info['lyrics']}"
            )
            bot.send_message(message.chat.id, song_info_message)
        except Exception:
            bot.send_message(message.chat.id, "Песня не найдена\n\nВыберите опцию:")
        finally:
            update_state(message, OPTIONS)

    @bot.message_handler(func=lambda message: get_state(message) == CHORDS)
    def handle_add_chords(message):
        song_title = CURRENT_SONG[message.from_user.username]
        update_song(message.from_user.username, song_title, "chords", message.text)
        update_state(message, STRUMMING)
        bot.send_message(message.chat.id, "Введите бой")

    @bot.message_handler(func=lambda message: get_state(message) == STRUMMING)
    def handle_add_strumming(message):
        song_title = CURRENT_SONG[message.from_user.username]
        update_song(message.from_user.username, song_title, "strumming", message.text)
        update_state(message, LYRICS)
        bot.send_message(message.chat.id, "Введите текст песни")

    @bot.message_handler(func=lambda message: get_state(message) == LYRICS)
    def handle_add_lyrics(message):
        song_title = CURRENT_SONG[message.from_user.username]
        update_song(message.from_user.username, song_title, "lyrics", message.text)
        update_state(message, OPTIONS)
        bot.send_message(message.chat.id, "Песня сохранена\n\nВыберите опцию:")

    bot.polling()
