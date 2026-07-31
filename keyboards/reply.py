from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎲 Tasodifiy"), KeyboardButton(text="🏆 Top multfilmlar")],
            [KeyboardButton(text="🔎 Qidiruv"), KeyboardButton(text="🎬 Multfilmlar")]
        ],
        resize_keyboard=True
    )
    return keyboard



def get_cancel_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )
    return keyboard
