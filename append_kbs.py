with open('keyboards/inline.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('InlineKeyboardButton(text="❌ Yopish", callback_data="delete_message")', 'InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel_open")')

admin_panel_kb = '''
def get_admin_panel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Multfilm yuklash", callback_data="admin_upload_multfilm"),
                InlineKeyboardButton(text="➕ Kino yuklash", callback_data="admin_upload_kino")
            ],
            [
                InlineKeyboardButton(text="✏️ Medialarni tahrirlash", callback_data="admin_edit_media"),
                InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton(text="📋 Baholar va Xabarlar", callback_data="admin_feedback_panel")
            ],
            [
                InlineKeyboardButton(text="⚙️ Obuna sozlash", callback_data="settings_forcesub_start"),
                InlineKeyboardButton(text="📝 Footer sozlash", callback_data="settings_footer_start")
            ],
            [
                InlineKeyboardButton(text="👑 Adminlar boshqaruvi", callback_data="settings_admins_start"),
                InlineKeyboardButton(text="🕵️ Baza Logi", callback_data="settings_stealth_start")
            ],
            [
                InlineKeyboardButton(text="❌ Yopish", callback_data="delete_message")
            ]
        ]
    )
'''

text = text + '\n' + admin_panel_kb

with open('keyboards/inline.py', 'w', encoding='utf-8') as f:
    f.write(text)
