from maxapi.context import State, StatesGroup

class RoomsFSM(StatesGroup):
    main = State()
    create = State()
    add = State()
    delete = State()
    generate = State()

class FSM(StatesGroup):
    main_menu = State()
    rooms = RoomsFSM()
    gifts = State()
