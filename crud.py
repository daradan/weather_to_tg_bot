import utils
from database import SessionLocal
from models import User, Settings, Location


def get_user(session, user_id) -> User:
    user = session.query(User).get(user_id)
    return user


def create_user(session, user) -> User:
    user = User(
        id=user.id,
        username=user.username,
        firstname=user.first_name,
        lastname=user.last_name,
    )
    session.add(user)
    session.commit()
    return user


def get_or_create_user(session, user_obj) -> User:
    user = get_user(session, user_id=user_obj.id)
    if not user:
        user = create_user(session, user_obj)
    return user


def get_location(session: SessionLocal, location_adr: str) -> Location:
    location: Location = session.query(Location).filter_by(city_raw=location_adr.lower()).first()
    return location


def add_location(session: SessionLocal, location_adr: str) -> Location:
    data: dict = utils.get_location(location_adr)
    location: Location = Location(
        city_raw=location_adr.lower(),
        city=data['city'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        timezone=data['timezone'],
        diff_time=data['diff_time']
    )
    session.add(location)
    session.commit()
    return location


def get_or_add_location(session, location_adr) -> Location:
    location: Location = get_location(session, location_adr)
    if not location:
        location: Location = add_location(session, location_adr)
    return location


def get_settings(session, user_id):
    settings = session.query(Settings).filter_by(user_id=user_id).all()
    return settings


def get_location_by_id(session, location_id) -> Location:
    locations = session.query(Location).filter_by(id=location_id).first()
    return locations


def get_setting_by_id(session, notification_id) -> Settings:
    setting = session.query(Settings).filter_by(id=notification_id).first()
    return setting


def get_settings_by_time(session, notification_time):
    settings = session.query(Settings).filter_by(notify_time=notification_time).all()
    return settings


def delete_setting_by_id(session, notification_id):
    session.query(Settings).filter_by(id=notification_id).delete()
    session.commit()


def create_settings(session, user_id, location_id, notify_time_raw, notify_time, language):
    settings = Settings(
        user_id=user_id,
        location_id=location_id,
        notify_time_raw=notify_time_raw,
        notify_time=notify_time,
        language=language
    )
    session.add(settings)
    session.commit()
