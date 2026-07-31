from aiogram.fsm.state import State, StatesGroup

class UploadContent(StatesGroup):
    title = State()
    files = State()
    year = State()
    quality = State()
    genre = State()
    keywords = State()

class AdminBroadcast(StatesGroup):
    message = State()

class AddAdmin(StatesGroup):
    user_id = State()

class SetForceSub(StatesGroup):
    channel_username = State()

class SetChannelLink(StatesGroup):
    channel_link = State()

class SetCustomFooter(StatesGroup):
    footer_text = State()

class ContactAdmin(StatesGroup):
    message = State()

class RateBot(StatesGroup):
    message = State()

class ReplyFeedback(StatesGroup):
    message = State()

class MediaEdit(StatesGroup):
    search_query = State()
    edit_video = State()
    edit_title = State()
    edit_year = State()
    edit_quality = State()
    edit_genre = State()

class SetMainChannelLink(StatesGroup):
    link = State()
