from database import SessionLocal
from models import User


def get_user(session, user_id) -> User:
    user = session.query(User).get(user_id)
    return user


def create_user(session, user) -> User:
    user = User(
        id=user.id,
        username=user.username,
        firstname=user.first_name,
        lastname=user.last_name,
        language='RU'
    )
    session.add(user)
    session.commit()
    return user
