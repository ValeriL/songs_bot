from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from bot.models import Song

Base = declarative_base()


class Database:
    def __init__(self, obj):
        engine = create_engine(obj, echo=False)
        session = sessionmaker(bind=engine)
        self.session = session()

    def add_song(self, song):
        existed_song = self.find_song(self, song.title)
        if existed_song:
            existed_song.chords = song.chords
            existed_song.strumming = song.strumming
            existed_song.lyrics = song.lyrics
        else:
            self.session.add(song)
        self.session.commit()

    def find_song(self, title):
        return self.session.query(Song).filter_by(title=title).first()
