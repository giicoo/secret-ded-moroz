import asyncio
import logging
from maxapi.types import Attachment, BotStarted, Command, MessageCreated, MessageCallback
from maxapi import Bot, Dispatcher, F
from maxapi.enums.parse_mode import ParseMode
from maxapi.context import MemoryContext, State, StatesGroup
from core.config import configs
from maxbot.fsm import FSM, RoomsFSM
from maxbot import keyboard
from repository.user import UserRepository
from repository.room import RoomRepository
from repository.gift import GiftRepository
from utils.utils import distribute_santa_gifts

logging.basicConfig(level=logging.INFO)

bot = Bot(configs.BOT_TOKEN)
dp = Dispatcher()

user_repo = UserRepository(configs.DB_URI)
rooms_repo = RoomRepository(configs.DB_URI)
gift_repo = GiftRepository(configs.DB_URI)

start_text = '''
💙**Мы комадна 3DOM и это наш бот "Секретный Дед Мороз"**
Суть игры такая:
1. Вы с друзьями или близкими создает комнату и добавляетесь туда
2. Кто-то из вас выбирает "Распределить подарки"
3. У каждого в меню подарков появляется человек, которому вы дарите подарок
'''


# ================= STARTUP =================
@dp.on_started()
async def _():
    logging.info("Бот стартовал!")

@dp.bot_started()
async def bot_started(event: BotStarted):
    user = user_repo.get_user_by_user_id(event.user.user_id)
    if not user:
        user_repo.create_user(event.user.user_id, str(event.user.first_name) + " " + str(event.user.last_name))

    await event.bot.send_message(
        chat_id=event.chat_id,
        text=start_text,
        parse_mode=ParseMode.MARKDOWN,
        attachments=[keyboard.get_start_keyboard()]
    )
# ==========================================

# ================== Главное меню ==================
@dp.message_created(Command("start"))
@dp.message_callback(F.callback.payload == "main_menu")
@dp.message_callback(F.callback.payload == "start")
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
    user = user_repo.get_user_by_user_id(event.get_ids()[1])
    rooms = user_repo.get_user_rooms(user.id)

    if rooms:
        text = "📋 Твои комнаты:\n"
        for idx, room in enumerate(rooms, start=1):
            text += f"{idx}. Комната (код: {room.invite_code})\n"
    else:
        text = "❌ У тебя пока нет комнат."

    await event.message.answer(text, attachments=[keyboard.get_room_keyboard()])


@dp.message_callback(F.callback.payload == "rooms_create")
async def rooms_create(event: MessageCallback, context: MemoryContext):
    room = rooms_repo.create_room()
    user = user_repo.get_user_by_user_id(event.get_ids()[1])
    user_repo.add_user_to_room(user.id, room.id)

    await event.message.answer(
        f"✅ Комната создана! Код: {room.invite_code}",
    )

    await rooms_main(event, context)


@dp.message_callback(F.callback.payload == "rooms_add")
async def rooms_add_start(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.rooms.add)
    await event.message.answer("🔢 Введи код комнаты для добавления:")


@dp.message_created(F.message.body.text, FSM.rooms.add)
async def rooms_add_code(event: MessageCreated, context: MemoryContext):
    code = event.message.body.text
    room = rooms_repo.get_room_by_invite_code(code)
    if not room:
        await event.message.answer(f'Комнаты с кодом {code} не существеует напиши другой код.')
    user = user_repo.get_user_by_user_id(event.get_ids()[1])
    user_repo.add_user_to_room(user.id, room.id)

    await event.message.answer(f"✅ Ты присоединился к комнате с кодом {code}!")

    await rooms_main(event, context)

# ====== УДАЛЕНИЕ ЧЕРЕЗ КНОПКИ ======
@dp.message_callback(F.callback.payload == 'rooms_delete_prompt')
async def rooms_delete_prompt(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.rooms.delete)  # остаёмся в меню комнат
    await event.message.answer(
        "Введите номер комнаты, которую хотите удалить (например, 1):"
    )

@dp.message_created(F.message.body.text, FSM.rooms.delete)
async def rooms_delete_by_number(event: MessageCreated, context: MemoryContext):
    user = user_repo.get_user_by_user_id(event.get_ids()[1])
    rooms = user_repo.get_user_rooms(user.id)


    idx = int(event.message.body.text) - 1
    if 0 <= idx < len(rooms):
        removed = rooms[idx]
        rooms_repo.delete_room(removed.id)
        await event.message.answer(f"❌ Комната «{idx+1}» удалена!")
    else:
        await event.message.answer("❌ Некорректный номер комнаты.")
    await rooms_main(event, context)


@dp.message_callback(F.callback.payload == "rooms_generate")
async def rooms_generate_start(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.rooms.generate)
    await event.message.answer("🔢 Введи код комнаты для распределения:")


@dp.message_created(F.message.body.text, FSM.rooms.generate)
async def rooms_generate(event: MessageCreated, context: MemoryContext):
    user = user_repo.get_user_by_user_id(event.get_ids()[1])
    rooms = user_repo.get_user_rooms(user.id)
    idx = int(event.message.body.text) - 1
    if 0 <= idx < len(rooms):
        users = rooms_repo.get_room_users(rooms[idx].id)
        rasp = distribute_santa_gifts([u.id for u in users])
        for sender in rasp:
            receiver = rasp[sender]
            gift_repo.create_gift(sender, receiver, rooms[idx].id)
        await event.message.answer(f"Подарки распределены!")
    else:
        await event.message.answer("❌ Некорректный номер комнаты.")
    await rooms_main(event, context)


# ================== Меню подарков ==================
@dp.message_callback(F.callback.payload == "gifts")
async def gifts_main(event: MessageCallback, context: MemoryContext):
    await context.set_state(FSM.gifts)
    user = user_repo.get_user_by_user_id(event.get_ids()[1])
    gifts = gift_repo.get_gifts_by_sender(user.id)

    if gifts:
        text = "🎁 Кому ты даришь подарки:\n\n"
        for g in gifts:
            text += f"• В комнате «{g.room.invite_code}» → {g.receiver.name}\n"
    else:
        text = "Пока нет комнат с распределёнными подарками."

    await event.message.answer(text, attachments=[keyboard.get_gifts_keyboard()])


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
