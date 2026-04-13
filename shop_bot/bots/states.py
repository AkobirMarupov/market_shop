from aiogram.fsm.state import StatesGroup, State

class ChatStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_comment = State()