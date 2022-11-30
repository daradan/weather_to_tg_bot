from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from database import Base, engine


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    username = Column(String, nullable=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)


class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    location = Column(String, nullable=True)
    notify_time = Column(String, nullable=True)
    language = Column(String)


Base.metadata.create_all(engine)
