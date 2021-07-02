import os
from collections import defaultdict

import telebot
from dotenv import load_dotenv
from logic import Database
from models import Song
from telebot import types


def get_song(user_id, title):
    return SONGS[user_id][title]


def update_song(username, title, key, value):
    SONGS[username][title][key] = value


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


if __name__ == "__main__":

    project_folder = os.path.expanduser("~/PycharmProjects/SongsLibBot")
    load_dotenv(os.path.join(project_folder, ".env"))

    db_link = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1) or "postgresql://%s:%s@%s/%s" % (
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_HOST"),
        os.getenv("DB_NAME"),
    )
    db = Database(db_link)

    bot = telebot.TeleBot(os.getenv("TOKEN"))

    START, OPTIONS, ADD_TITLE, FIND_TITLE, CHORDS, STRUMMING, LYRICS = range(7)
    USER_STATE = defaultdict(lambda: START)
    CURRENT_SONG = defaultdict(str)

    SONGS = defaultdict(lambda: {})

    @bot.message_handler(commands=["start"])
    @bot.message_handler(func=lambda message: get_state(message) == START)
    def handle_message(message):
        db.add_user(message.from_user.username)

        keyboard = types.ReplyKeyboardMarkup(True)
        add_song_button = types.KeyboardButton("Добавить песню")
        find_song_button = types.KeyboardButton("Найти песню")
        keyboard.row(add_song_button, find_song_button)

        update_state(message, OPTIONS)
        bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=keyboard)

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
            song_info = db.find_song(db.find_user(message.from_user.username), message.text)
            song_info_message = (
                f"Название:\n{message.text}\n\nАккорды:\n{song_info.chords}\n\n"
                f"Бой:\n{song_info.strumming}\n\nТекст:\n{song_info.lyrics}\n\nВыберите опцию:"
            )
            bot.send_message(message.chat.id, song_info_message)
        except Exception as error:
            print(error)
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
        user = message.from_user.username
        user_id = db.find_user(user)

        song_title = CURRENT_SONG[user]

        update_song(user, song_title, "lyrics", message.text)
        update_state(message, OPTIONS)

        song = get_song(user, song_title)
        new_song = Song(
            user_id=user_id,
            title=song_title,
            chords=song["chords"],
            strumming=song["strumming"],
            lyrics=song["lyrics"],
        )

        db.add_song(user_id, new_song)
        CURRENT_SONG[user] = defaultdict(str)
        bot.send_message(message.chat.id, "Песня сохранена\n\nВыберите опцию:")

    bot.polling()
