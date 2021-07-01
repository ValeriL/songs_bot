from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from bot.models import Song, User

Base = declarative_base()


class Database:
    def __init__(self, obj):
        engine = create_engine(obj, echo=False)
        session = sessionmaker(bind=engine)
        self.session = session()

    def add_song(self, user_id, song):
        existed_song = self.find_song(user_id, song.title)
        if existed_song:
            existed_song.chords = song.chords
            existed_song.strumming = song.strumming
            existed_song.lyrics = song.lyrics
        else:
            self.session.add(song)
        self.session.commit()

    def find_song(self, user_id, title):
        return self.session.query(Song).filter_by(user_id=user_id, title=title).first()

    def add_user(self, username):
        existed_user = self.find_user(username)
        if not existed_user:
            self.session.add(User(username=username))
            self.session.commit()

    def find_user(self, username):
        return self.session.query(User).filter_by(username=username).first().id
