from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import and_
from sqlalchemy.exc import SQLAlchemyError
from model.models import User, Room, room_user
from repository.base import BaseRepository
import logging

class UserRepository(BaseRepository):
    def __init__(self, database_url: str):
        super().__init__(database_url)

    def create_user(self, user_id: int) -> Optional[User]:
        with self.get_session() as session:
            try:
                user = User(user_id=user_id)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(e)
                return None

    def add_user_to_room(self, user_id: int, room_id: int) -> bool:
        with self.get_session() as session:
            try:
                user = session.get(User, user_id)
                room = session.get(Room, room_id)
                if user and room:
                    user.rooms.append(room)
                    session.commit()
                    return True
                return False
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(e)
                return False

    def remove_user_from_room(self, user_id: int, room_id: int) -> bool:
        with self.get_session() as session:
            try:
                user = session.get(User, user_id, options=[selectinload(User.rooms)])
                if user and any(room.id == room_id for room in user.rooms):
                    user.rooms = [room for room in user.rooms if room.id != room_id]
                    session.commit()
                    return True
                return False
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(e)
                return False

    def get_user_by_id(self, id: int) -> Optional[User]:
        with self.get_session() as session:
            return session.get(User, id, options=[selectinload(User.rooms)])

    def get_user_by_user_id(self, user_id: int) -> Optional[User]:
        with self.get_session() as session:
            return session.execute(
                select(User)
                .where(User.user_id == user_id)
                .options(selectinload(User.rooms))
            ).scalar_one_or_none()

    def get_users_in_room(self, room_id: int) -> List[User]:
        with self.get_session() as session:
            return list(session.execute(
                select(User)
                .join(User.rooms)
                .where(Room.id == room_id)
                .options(selectinload(User.rooms))
            ).scalars().all())

    def get_user_rooms(self, user_id: int) -> List[Room]:
        with self.get_session() as session:
            user = session.get(User, user_id, options=[selectinload(User.rooms)])
            return user.rooms if user else []

    def user_in_room(self, user_id: int, room_id: int) -> bool:
        with self.get_session() as session:
            result = session.execute(
                select(room_user)
                .where(
                    and_(
                        room_user.c.user_id == user_id,
                        room_user.c.room_id == room_id
                    )
                )
            ).first()
            return result is not None
