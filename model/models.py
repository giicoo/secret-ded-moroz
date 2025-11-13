from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from utils.utils import code_generator
Base = declarative_base()

room_user = Table(
    'room_user',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('room_id', Integer, ForeignKey('rooms.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    # Relationships (многие-ко-многим с Room)
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        secondary=room_user,
        back_populates="users"
    )
    sent_gifts: Mapped[list["Gift"]] = relationship(
        "Gift",
        foreign_keys="Gift.sender_id",
        back_populates="sender"
    )
    received_gifts: Mapped[list["Gift"]] = relationship(
        "Gift",
        foreign_keys="Gift.receiver_id",
        back_populates="receiver"
    )

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    invite_code: Mapped[str] = mapped_column(String, default=code_generator)

    # Relationships (многие-ко-многим с User)
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=room_user,
        back_populates="rooms"
    )
    gifts: Mapped[list["Gift"]] = relationship("Gift", back_populates="room")

class Gift(Base):
    __tablename__ = "gifts"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey('rooms.id'))

    # Relationships
    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_gifts"
    )
    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_gifts"
    )
    room: Mapped["Room"] = relationship("Room", back_populates="gifts")
