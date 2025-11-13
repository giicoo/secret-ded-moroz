from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import Attachment, CallbackButton


def get_main_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(
        CallbackButton(
            text='Комнаты',
            payload='rooms'
        )
    )

    builder.row(
        CallbackButton(
            text='Подарки',
            payload='gifts'
        )
    )

    return builder.as_markup()

def get_room_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(
        CallbackButton(
            text='Создать',
            payload='rooms_create'
        )
    )

    builder.row(
        CallbackButton(
            text='Присоединиться',
            payload='rooms_add'
        )
    )

    builder.row(
        CallbackButton(
            text='Главное меню',
            payload='main_menu'
        )
    )

    return builder.as_markup()

def get_gifts_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(
        CallbackButton(
            text='Главное меню',
            payload='main_menu'
        )
    )

    return builder.as_markup()

def get_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(
        CallbackButton(
            text='Главное меню',
            payload='main_menu'
        )
    )

    return builder.as_markup()


def get_rooms_list_keyboard(rooms: list) -> Attachment:
    builder = InlineKeyboardBuilder()

    for idx, room in enumerate(rooms):
        builder.row(
            CallbackButton(
                text=f"Удалить «{room['name']}»",
                payload=f"rooms_delete_{idx}"  # строка!
            )
        )

    # Кнопка назад
    builder.row(
        CallbackButton(
            text="⬅️ Назад",
            payload="rooms"
        )
    )

    return builder.as_markup()
