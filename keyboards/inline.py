from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse

def get_start_menu(is_admin: bool, channel_link: str):
    link = channel_link if channel_link else "https://t.me/telegram"
    inline_keyboard = [
        [
            InlineKeyboardButton(text="🎲 Tasodifiy", callback_data="start_random"),
            InlineKeyboardButton(text="🏆 Top multfilmlar", callback_data="start_top")
        ],
        [
            InlineKeyboardButton(text="🔎 Qidiruv", callback_data="start_search"),
            InlineKeyboardButton(text="🎬 Multfilmlar", url=link)
        ]
    ]
    if is_admin:
        inline_keyboard.append([InlineKeyboardButton(text="⚙️ Admin Paneli", callback_data="admin_panel_open")])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_content_inline_keyboard(content_code: int, bot_username: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="♻️ Do'stlarga ulashish",
                    url=f"https://t.me/share/url?url=https://t.me/{bot_username}?start={content_code}&text=Ushbu ajoyib multfilm/kinoni ko'rishni tavsiya qilaman! Uni ko'rish uchun ustiga bosing:"
                )
            ]
        ]
    )

def get_genre_selection_keyboard(selected_genres: list):
    genres = ["💥 Jangari", "😂 Komediya", "🧙‍♂️ Fantastika", "🏃‍♂️ Sarguzasht", "👨‍👩‍👧‍👦 Oila", "🌟 Animatsiya", "🐉 Anime"]
    inline_keyboard = []
    row = []
    for g in genres:
        text = f"✅ {g}" if g in selected_genres else g
        row.append(InlineKeyboardButton(text=text, callback_data=f"genre_{g}"))
        if len(row) == 2:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)
        
    inline_keyboard.append([InlineKeyboardButton(text="🏁 Saqlash va Davom etish", callback_data="genre_done")])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_force_sub_keyboard(channel_link: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=channel_link)],
            [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")]
        ]
    )

def get_admin_fsm_skip_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data="fsm_skip")]
        ]
    )

def get_admin_fsm_done_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Barchasi tashlandi", callback_data="fsm_files_done")]
        ]
    )

def get_top_content_keyboard(content_list):
    keyboard = []
    row = []
    for i, _ in enumerate(content_list, start=1):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"get_top_{i-1}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_search_results_keyboard(results):
    keyboard = []
    for res in results:
        ctype = "🍿" if res['type'] == 'multfilm' else "🎬"
        keyboard.append([InlineKeyboardButton(text=f"{ctype} {res['name']}", callback_data=f"get_content_{res['code']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_feedback_reply_keyboard(feedback_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_feedback_{feedback_id}")]
        ]
    )

def get_rating_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1⭐️", callback_data="rate_1"),
                InlineKeyboardButton(text="2⭐️", callback_data="rate_2"),
                InlineKeyboardButton(text="3⭐️", callback_data="rate_3"),
                InlineKeyboardButton(text="4⭐️", callback_data="rate_4"),
                InlineKeyboardButton(text="5⭐️", callback_data="rate_5")
            ]
        ]
    )

def get_share_keyboard(bot_username: str):
    text = (
        "Bot menga judayam yoqdi, ichida menga yoqqan juda ko'p multfilm va filmlar bor ekan, sizlarga ham tavsiya qilaman, tezda kiring: 👇\n\n"
        f"https://t.me/{bot_username}\n"
        f"https://t.me/{bot_username}\n"
        f"https://t.me/{bot_username}"
    )
    encoded_text = urllib.parse.quote(text)
    url = f"https://t.me/share/url?url=https://t.me/{bot_username}&text={encoded_text}"
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 Do'stlarga ulashish", url=url)]
        ]
    )

def get_feedback_manager_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ Baholarni ko'rish", callback_data="view_fb_rate"),
                InlineKeyboardButton(text="📩 Xabarlarni ko'rish", callback_data="view_fb_contact")
            ]
        ]
    )

def get_feedback_item_keyboard(f_type: str, item_id: int, current_index: int, total_count: int):
    nav_row = []
    if current_index > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Oldingisi", callback_data=f"nav_fb_{f_type}_{current_index-1}"))
    
    nav_row.append(InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del_fb_{f_type}_{item_id}_{current_index}"))
    
    if current_index < total_count - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingisi ▶️", callback_data=f"nav_fb_{f_type}_{current_index+1}"))
        
    return InlineKeyboardMarkup(
        inline_keyboard=[
            nav_row,
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel_open")]
        ]
    )

def get_media_type_selection_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🍿 Multfilmlarni tahrirlash", callback_data="edit_media_type_multfilm"),
                InlineKeyboardButton(text="🎬 Kinolarni tahrirlash", callback_data="edit_media_type_kino")
            ]
        ]
    )

def get_media_pagination_keyboard(items, page: int, total_pages: int, ctype: str):
    keyboard = []
    for i, item in enumerate(items, start=1):
        keyboard.append([InlineKeyboardButton(text=f"{i}. {item['name']} ({item['code']})", callback_data=f"edit_media_item_{item['id']}_{page}")])
        
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"edit_media_page_{ctype}_{page-1}"))
    else:
        nav_row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        
    nav_row.append(InlineKeyboardButton(text=f"Sahifa {page}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="Keyingisi ▶️", callback_data=f"edit_media_page_{ctype}_{page+1}"))
    else:
        nav_row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        
    keyboard.append(nav_row)
    keyboard.append([
        InlineKeyboardButton(text="🔎 Nom bo'yicha qidirish", callback_data=f"edit_media_search_{ctype}"),
        InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_panel_open")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_media_edit_dashboard_keyboard(content_id: int, ctype: str, return_page: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📹 Videoni almashtirish", callback_data=f"edit_media_f_video_{content_id}_{return_page}"),
                InlineKeyboardButton(text="📝 Nomin tahrirlash", callback_data=f"edit_media_f_name_{content_id}_{return_page}")
            ],
            [
                InlineKeyboardButton(text="📅 Yilni tahrirlash", callback_data=f"edit_media_f_year_{content_id}_{return_page}"),
                InlineKeyboardButton(text="🎭 Janrni tahrirlash", callback_data=f"edit_media_f_genre_{content_id}_{return_page}")
            ],
            [
                InlineKeyboardButton(text="✨ Sifatni tahrirlash", callback_data=f"edit_media_f_quality_{content_id}_{return_page}"),
                InlineKeyboardButton(text="🗑 Mediani to'liq o'chirish", callback_data=f"edit_media_del_{content_id}_{return_page}")
            ],
            [
                InlineKeyboardButton(text="🔙 Siyohiga (Ro'yxatga) qaytish", callback_data=f"edit_media_page_{ctype}_{return_page}")
            ]
        ]
    )

def get_delete_confirm_keyboard(content_id: int, return_page: int, ctype: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, o'chirilsin", callback_data=f"del_confirm_{content_id}_{return_page}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"edit_media_item_{content_id}_{return_page}")
            ]
        ]
    )
