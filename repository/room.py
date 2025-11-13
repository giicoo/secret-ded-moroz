from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from model.models import Room, User, room_user
from repository.base import BaseRepository
import logging

class RoomRepository(BaseRepository):
    def __init__(self, database_url: str):
        super().__init__(database_url)

    def create_room(self) -> Optional[Room]:
        with self.get_session() as session:
            try:
                room = Room()
                session.add(room)
                session.commit()
                session.refresh(room)
                return room
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(e)
                return None

    def get_room_by_id(self, room_id: int) -> Optional[Room]:
        with self.get_session() as session:
            return session.get(Room, room_id, options=[selectinload(Room.users), selectinload(Room.gifts)])

    def get_room_by_invite_code(self, invite_code: str) -> Optional[Room]:
        with self.get_session() as session:
            return session.execute(
                select(Room)
                .where(Room.invite_code == invite_code)
                .options(selectinload(Room.users), selectinload(Room.gifts))
            ).scalar_one_or_none()

    def delete_room(self, room_id: int) -> bool:
        with self.get_session() as session:
            try:
                session.execute(
                    delete(Room).where(Room.id == room_id)
                )
                session.commit()
                return True
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(e)
                return False

    def get_room_users(self, room_id: int) -> List[User]:
        with self.get_session() as session:
            room = session.get(Room, room_id, options=[selectinload(Room.users)])
            return room.users if room else []

    def room_has_users(self, room_id: int) -> bool:
        with self.get_session() as session:
            count = session.execute(
                select(room_user.c.user_id)
                .where(room_user.c.room_id == room_id)
            ).first()
            return count is not None
