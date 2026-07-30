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

def get_admin_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Multfilm yuklash"), KeyboardButton(text="➕ Kino yuklash")],
            [KeyboardButton(text="✏️ Medialarni tahrirlash")],
            [KeyboardButton(text="📢 Xabar yuborish (Broadcast)")],
            [KeyboardButton(text="📋 Baholar va Xabarlar boshqaruv paneli")],
            [KeyboardButton(text="⚙️ Majburiy obuna sozlash"), KeyboardButton(text="📝 Footer sozlash")],
            [KeyboardButton(text="👑 Adminlar boshqaruvi"), KeyboardButton(text="⚙️ Baza Sozlamalari")],
            [KeyboardButton(text="🔙 Asosiy menyu")]
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
