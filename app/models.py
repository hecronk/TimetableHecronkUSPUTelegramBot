from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

Base = declarative_base()
engine = create_engine('sqlite:///sqlite3.db', echo=True)
Base.metadata.bind = engine
session = scoped_session(sessionmaker())(bind=engine)


class User(Base):
    __tablename__ = 'User'

    code = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    group = Column(String(250))

    def __repr__(self):
        return '<User {}>'.format(self.code)


Base.metadata.create_all(engine)
