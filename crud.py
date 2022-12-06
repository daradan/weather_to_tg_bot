from database import SessionLocal
from models import User, Settings


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


def get_settings(session, user_id):
    settings = session.query(Settings).filter_by(user_id=user_id).all()
    return settings


def get_setting_by_id(session, notification_id):
    setting = session.query(Settings).filter_by(id=notification_id).first()
    return setting


def get_settings_by_time(session, notification_time):
    settings = session.query(Settings).filter_by(notify_time=notification_time).all()
    return settings


def delete_setting_by_id(session, notification_id):
    session.query(Settings).filter_by(id=notification_id).delete()
    session.commit()


def create_settings(session, user_id, location, notify_time):
    settings = Settings(
        user_id=user_id,
        location=location,
        notify_time=notify_time,
        language='RU'
    )
    session.add(settings)
    session.commit()
