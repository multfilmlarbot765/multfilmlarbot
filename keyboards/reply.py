from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def get_user_main_menu(is_admin=False):
    if is_admin:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⚙️ Admin paneli")]
            ],
            resize_keyboard=True
        )
    return ReplyKeyboardRemove()
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

def get_admin_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Multfilm yuklash"), KeyboardButton(text="➕ Kino yuklash")],
            [KeyboardButton(text="✏️ Medialarni tahrirlash"), KeyboardButton(text="📢 Broadcast")],
            [KeyboardButton(text="📋 Baholar va Xabarlar"), KeyboardButton(text="⚙️ Obuna sozlash")],
            [KeyboardButton(text="📝 Footer sozlash"), KeyboardButton(text="👑 Adminlar boshqaruvi")],
            [KeyboardButton(text="🗄 Baza Logi"), KeyboardButton(text="🔗 Kanal havolasini sozlash")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="❌ Yopish")]
        ],
        resize_keyboard=True
    )
    return keyboard
