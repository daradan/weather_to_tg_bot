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


class Location(Base):
    __tablename__ = "location"
    id = Column(Integer, primary_key=True, index=True)
    city_raw = Column(String, nullable=True)
    city = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    diff_time = Column(String, nullable=True)


class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    location_id = Column(Integer, ForeignKey(Location.id), nullable=True)
    notify_time_raw = Column(String, nullable=True)
    notify_time = Column(String, nullable=True)
    language = Column(String, nullable=True)


Base.metadata.create_all(engine)
