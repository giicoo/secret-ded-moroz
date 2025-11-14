from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import Attachment, CallbackButton

def get_start_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(CallbackButton(text="Начать", payload="start"))

    return builder.as_markup()

def get_main_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(CallbackButton(text='Комнаты', payload='rooms'))
    builder.row(CallbackButton(text='Подарки', payload='gifts'))

    return builder.as_markup()

def get_room_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(CallbackButton(text='Создать', payload='rooms_create'))
    builder.row(CallbackButton(text='Присоединиться', payload='rooms_add'))
    builder.row(CallbackButton(text='Удалить комнату', payload='rooms_delete_prompt'))
    builder.row(CallbackButton(text='Распределить подарки', payload='rooms_generate'))
    builder.row(CallbackButton(text='Главное меню', payload='main_menu'))

    return builder.as_markup()

def get_gifts_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(CallbackButton(text='Главное меню',payload='main_menu'))

    return builder.as_markup()

def get_keyboard() -> Attachment:
    builder = InlineKeyboardBuilder()

    builder.row(CallbackButton(text='Главное меню',payload='main_menu'))

    return builder.as_markup()


def get_rooms_list_keyboard(rooms: list) -> Attachment:
    builder = InlineKeyboardBuilder()

    for idx, room in enumerate(rooms):
        builder.row(CallbackButton(text=f"Удалить «{room['name']}»", payload=f"rooms_delete_{idx}"))

    builder.row(CallbackButton(text="⬅️ Назад",payload="rooms"))

    return builder.as_markup()
