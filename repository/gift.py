from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import and_
from sqlalchemy.exc import SQLAlchemyError
from model.models import Gift, room_user
from repository.base import BaseRepository
import logging


class GiftRepository(BaseRepository):
    def __init__(self, database_url: str):
        super().__init__(database_url)

    def create_gift(self, sender_id: int, receiver_id: int, room_id: int) -> Optional[Gift]:
        with self.get_session() as session:
            try:
                # Проверяем, что оба пользователя в одной комнате
                sender_in_room = session.execute(
                    select(room_user)
                    .where(
                        and_(
                            room_user.c.user_id == sender_id,
                            room_user.c.room_id == room_id
                        )
                    )
                ).first()

                receiver_in_room = session.execute(
                    select(room_user)
                    .where(
                        and_(
                            room_user.c.user_id == receiver_id,
                            room_user.c.room_id == room_id
                        )
                    )
                ).first()

                if not sender_in_room or not receiver_in_room:
                    return None

                gift = Gift(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    room_id=room_id
                )
                session.add(gift)
                session.commit()
                session.refresh(gift)
                return gift
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(e)
                return None

    def get_gift_by_id(self, gift_id: int) -> Optional[Gift]:
        with self.get_session() as session:
            return session.get(Gift, gift_id, options=[selectinload(Gift.sender), selectinload(Gift.receiver), selectinload(Gift.room)])

    def get_gifts_by_sender(self, sender_id: int) -> List[Gift]:
        with self.get_session() as session:
            return list(session.execute(
                select(Gift)
                .where(Gift.sender_id == sender_id)
                .options(selectinload(Gift.sender), selectinload(Gift.receiver), selectinload(Gift.room))
            ).scalars().all())

    def get_gifts_by_receiver(self, receiver_id: int) -> List[Gift]:
        with self.get_session() as session:
            return list(session.execute(
                select(Gift)
                .where(Gift.receiver_id == receiver_id)
                .options(selectinload(Gift.sender), selectinload(Gift.receiver), selectinload(Gift.room))
            ).scalars().all())

    def get_gifts_in_room(self, room_id: int) -> List[Gift]:
        with self.get_session() as session:
            return list(session.execute(
                select(Gift)
                .where(Gift.room_id == room_id)
                .options(selectinload(Gift.sender), selectinload(Gift.receiver), selectinload(Gift.room))
            ).scalars().all())
