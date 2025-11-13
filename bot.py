import asyncio
import logging
from keyboards import keyboard
from maxapi.types import Attachment, BotStarted, Command, MessageCreated, CallbackButton, MessageCallback, BotCommand
from maxapi import Bot, Dispatcher, F
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from core.config import configs


logging.basicConfig(level=logging.INFO)

bot = Bot(configs.BOT_TOKEN)
dp = Dispatcher()


start_text = '''Пример чат-бота для MAX 💙'''


# ================= FSM =================
class CreateRoomFSM(StatesGroup):
    name = State()

class AddRoomFSM(StatesGroup):
    code = State()

class RoomsFSM(StatesGroup):
    main = State()
    create = CreateRoomFSM()
    add = AddRoomFSM()
    delete = State()

class FSM(StatesGroup):
    main_menu = State()
    rooms = RoomsFSM()
    gifts = State()
# ======================================

# ================= STARTUP =================
@dp.on_started()
async def _():
    logging.info("Бот стартовал!")

@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Привет! Отправь мне /start"
    )
# ==========================================

# ================== HELPERS ==================
def generate_room_code():
    import random
    return str(random.randint(1000, 9999))
# =============================================

# ================== Главное меню ==================
@dp.message_created(Command("start"))
@dp.message_callback(F.callback.payload == "main_menu")
async def main_menu(event: MessageCreated, context: MemoryContext):
    await context.set_state(FSM.main_menu)
    await event.message.answer(
        "🏠 Главное меню:",
        attachments=[keyboard.get_main_keyboard()]
    )
# ==================================================

# ================== Меню комнат ==================
@dp.message_callback(F.callback.payload == 'rooms')
async def rooms_main(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.rooms.main)
    data = await context.get_data()
    rooms = data.get("rooms", [])

    if rooms:
        text = "📋 Твои комнаты:\n"
        for idx, room in enumerate(rooms, start=1):
            text += f"{idx}. {room['name']} (код: {room['code']})\n"
    else:
        text = "❌ У тебя пока нет комнат."

    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text='Создать', payload='rooms_create'))
    builder.row(CallbackButton(text='Присоединиться', payload='rooms_add'))
    builder.row(CallbackButton(text='Удалить комнату', payload='rooms_delete_prompt'))
    builder.row(CallbackButton(text='Главное меню', payload='main_menu'))

    await event.message.answer(text, attachments=[builder.as_markup()])


@dp.message_callback(F.callback.payload == "rooms_create")
async def rooms_create_start(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.rooms.create.name)
    await event.message.answer("✏️ Введи название новой комнаты:")


@dp.message_created(F.message.body.text, FSM.rooms.create.name)
async def rooms_create_name(event: MessageCreated, context: MemoryContext):
    room_name = event.message.body.text
    code = generate_room_code()

    data = await context.get_data()
    rooms = data.get("rooms", [])
    rooms.append({"name": room_name, "code": code})
    await context.update_data(rooms=rooms)

    await context.set_state(FSM.rooms.main)
    await event.message.answer(
        f"✅ Комната «{room_name}» создана! Код: {code}",
        attachments=[keyboard.get_room_keyboard()]
    )


@dp.message_callback(F.callback.payload == "rooms_add")
async def rooms_add_start(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.rooms.add.code)
    await event.message.answer("🔢 Введи код комнаты для добавления:")


@dp.message_created(F.message.body.text, FSM.rooms.add.code)
async def rooms_add_code(event: MessageCreated, context: MemoryContext):
    code = event.message.body.text
    data = await context.get_data()
    rooms = data.get("rooms", [])

    if any(r["code"] == code for r in rooms):
        await event.message.answer("❌ Ты уже добавлен в эту комнату.")
    else:
        rooms.append({"name": f"Комната {code}", "code": code})
        await context.update_data(rooms=rooms)
        await event.message.answer(f"✅ Ты присоединился к комнате с кодом {code}!")

    await context.set_state(FSM.rooms.main)
    await event.message.answer(attachments=[keyboard.get_room_keyboard()])


# ====== УДАЛЕНИЕ ЧЕРЕЗ КНОПКИ ======
@dp.message_callback(F.callback.payload == 'rooms_delete_prompt')
async def rooms_delete_prompt(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.rooms.delete)  # остаёмся в меню комнат
    await event.message.answer(
        "Введите номер комнаты, которую хотите удалить (например, 1):"
    )

@dp.message_created(F.message.body.text, FSM.rooms.delete)
async def rooms_delete_by_number(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()
    rooms = data.get("rooms", [])

    try:
        idx = int(event.message.body.text) - 1
        if 0 <= idx < len(rooms):
            removed = rooms.pop(idx)
            await context.update_data(rooms=rooms)
            await event.message.answer(f"❌ Комната «{removed['name']}» удалена!")
        else:
            await event.message.answer("❌ Некорректный номер комнаты.")
    except ValueError:
        # Если пользователь ввёл не число, игнорируем
        return

    # Показать обновлённое меню комнат
    await rooms_main(event, context)
# ================== Меню подарков ==================
@dp.message_callback(F.callback.payload == "gifts")
async def gifts_main(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.gifts)
    # Пример подарков (можно заменить на реальную логику)
    gifts_data = [
        {"room": "Новый год 🎄", "target": "Алексей"},
        {"room": "ДР Иры 🎂", "target": "Ира"},
    ]

    if gifts_data:
        text = "🎁 Кому ты даришь подарки:\n\n"
        for g in gifts_data:
            text += f"• В комнате «{g['room']}» → {g['target']}\n"
    else:
        text = "Пока нет комнат с распределёнными подарками."

    await event.message.answer(text, attachments=[keyboard.get_gifts_keyboard()])

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
