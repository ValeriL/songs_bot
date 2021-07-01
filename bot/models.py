import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Steps(enum.Enum):
    START = 1
    OPTIONS = 2
    ADD_TITLE = 3
    CHORDS = 4
    STRUMMING = 5
    LYRICS = 6
    FIND_TITLE = 7


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=False, unique=True)
    last_step = Column(Enum(Steps), nullable=False, default=Steps.START)
    children = relationship("Song")

    def __repr__(self):
        return f"<User(username={self.username}, last_step={self.last_step})>"


class Song(Base):

    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100), nullable=False, unique=True)
    chords = Column(String)
    strumming = Column(String)
    lyrics = Column(String)

    def __repr__(self):
        return f"<Song(username={self.user_id}, title={self.title}, chords={self.chords})>"
