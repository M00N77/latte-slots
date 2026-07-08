from aiogram.fsm.state import State, StatesGroup


class AddMeeting(StatesGroup):
    title = State()
    participants = State()
    date = State()
    start_time = State()
    end_time = State()


class AdsAnalysis(StatesGroup):
    waiting_file = State()
