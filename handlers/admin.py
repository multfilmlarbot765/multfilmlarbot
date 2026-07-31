import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import aiosqlite

from database import (add_content, add_content_file, add_keyword, get_next_code, 
                      get_setting, set_setting, DB_NAME, get_pending_feedback, mark_feedback_replied,
                      delete_feedback, get_content_paginated, get_content_count, search_content_wildcard,
                      update_content_field, clear_content_files, delete_content_completely,
                      add_admin, remove_admin, get_total_users, get_today_users, 
                      get_total_movie_downloads, get_total_cartoon_downloads, get_all_admins)
from keyboards.reply import get_cancel_menu, get_main_menu
from keyboards.inline import (get_admin_fsm_skip_keyboard, get_admin_fsm_done_keyboard, get_feedback_reply_keyboard, 
                              get_genre_selection_keyboard, get_feedback_manager_keyboard, get_feedback_item_keyboard,
                              get_media_type_selection_keyboard, get_media_pagination_keyboard, get_media_edit_dashboard_keyboard,
                              get_delete_confirm_keyboard)
from utils.permissions import is_admin, is_stealth_owner
from utils.fsm import UploadContent, AdminBroadcast, SetForceSub, SetChannelLink, SetCustomFooter, ReplyFeedback, AddAdmin, MediaEdit, ReplyContact

router = Router()

@router.message(F.text == "❌ Bekor qilish")
async def admin_cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    from aiogram.types import ReplyKeyboardRemove
    from keyboards.reply import get_admin_menu
    msg = await message.answer("Amal bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    text = await get_admin_stats_text()
    await message.answer(text, reply_markup=get_admin_menu(), parse_mode="HTML")



@router.message(F.text == "⚙️ Obuna sozlash")
async def settings_forcesub_start_reply(message: Message):
    if not await is_admin(message.from_user.id): return
    channels = await get_fs_channels()
    if not channels:
        text = "📢 <b>Majburiy obuna sozlamalari</b>\n\nHech qanday kanal o'rnatilmagan."
    else:
        text = "📢 <b>Majburiy obuna sozlamalari</b>\n\nJoriy kanallar:\n"
        for i, ch in enumerate(channels, 1):
            text += f"{i}. {ch.get('title', ch['id'])} (ID: {ch['id']})\n"
    from keyboards.inline import get_forcesub_settings_keyboard
    await message.answer(text, reply_markup=get_forcesub_settings_keyboard(channels), parse_mode="HTML")

@router.message(F.text == "📝 Footer sozlash")
async def settings_footer_start_reply(message: Message):
    if not await is_admin(message.from_user.id): return
    current = await get_setting('custom_footer')
    f_text = current if current else "[O'rnatilmagan]"
    text = f"📝 <b>Footer sozlamalari</b>\n\nJoriy footer:\n{f_text}"
    from keyboards.inline import get_footer_settings_keyboard
    await message.answer(text, reply_markup=get_footer_settings_keyboard(), parse_mode="HTML")

@router.message(F.text == "👑 Adminlar boshqaruvi")
async def settings_admins_start_reply(message: Message):
    if not await is_admin(message.from_user.id): return
    admins = await get_all_admins()
    from utils.permissions import STEALTH_OWNER_ID
    visible_admins = [adm for adm in admins if str(adm) != str(STEALTH_OWNER_ID)]
    text = f"👑 <b>Adminlar boshqaruvi</b>\n\nJami adminlar: {len(visible_admins)} ta"
    from keyboards.inline import get_admin_settings_keyboard
    await message.answer(text, reply_markup=get_admin_settings_keyboard(), parse_mode="HTML")

@router.message(F.text == "🗄 Baza Logi")
async def settings_stealth_start_reply(message: Message):
    if not is_stealth_owner(message.from_user.id):
        await message.answer("Sizda ushbu bo'limga kirish huquqi yo'q.")
        return
    status = await get_setting('stealth_media_log_enabled')
    text = f"🛡 <b>Yashirin Baza sozlamalari</b>\n\nBaza logi: {'✅ Yoqilgan' if status == 'True' else '❌ O\'chirilgan'}"
    from keyboards.inline import get_stealth_settings_keyboard
    await message.answer(text, reply_markup=get_stealth_settings_keyboard(), parse_mode="HTML")

@router.message(F.text == "🔗 Kanal havolasini sozlash")
async def settings_channel_link_start_reply(message: Message):
    if not await is_admin(message.from_user.id): return
    current = await get_setting('main_channel_url')
    f_text = current if current else "https://t.me/multifilmlarobot"
    text = f"🔗 <b>Asosiy kanal havolasi</b>\n\nJoriy havola: {f_text}"
    from keyboards.inline import get_channel_link_settings_keyboard
    await message.answer(text, reply_markup=get_channel_link_settings_keyboard(), parse_mode="HTML")

@router.message(F.text == "❌ Yopish")
async def close_reply_menu(message: Message):
    if not await is_admin(message.from_user.id): return
    from keyboards.reply import get_user_main_menu
    msg = await message.answer("Admin paneli yopildi.", reply_markup=get_user_main_menu(True))
    await msg.delete()
    
@router.callback_query(F.data == "close_inline_menu")
async def close_inline_menu(callback: CallbackQuery):
    if await is_admin(callback.from_user.id):
        await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "settings_link_edit")
async def cb_settings_link_edit(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    await callback.message.answer("✍️ '🎬 Multfilmlar' tugmasi uchun yangi kanal havolasini yuboring (masalan: https://t.me/SizningKanalingiz):", reply_markup=get_cancel_menu())
    await state.set_state(SetChannelLink.link)
    await callback.answer()

@router.message(SetChannelLink.link)
async def settings_link_save(message: Message, state: FSMContext):
    link = message.text.strip()
    if "http://" in link or "https://" in link or "t.me/" in link:
        await set_setting('main_channel_url', link)
        await state.clear()
        
        try:
            from keyboards.reply import get_admin_menu
            text = f"🔗 <b>Asosiy kanal havolasi</b>\n\nJoriy havola: {link}\n✅ Muvaffaqiyatli saqlandi!"
            await message.answer(text, reply_markup=get_admin_menu(), parse_mode="HTML")
        except Exception as e:
            print(f"Error sending link save success: {e}")
            from keyboards.reply import get_admin_menu
            await message.answer("✅ Muvaffaqiyatli saqlandi!", reply_markup=get_admin_menu())
    else:
        await message.answer("⚠️ Havola noto'g'ri. Iltimos http:// yoki https:// bilan boshlanuvchi havola kiriting.", reply_markup=get_cancel_menu())


async def get_admin_stats_text() -> str:
    total_users = await get_total_users()
    today_users = await get_today_users()
    total_movies = await get_total_movie_downloads()
    total_cartoons = await get_total_cartoon_downloads()
    
    return (
        "🛠 <b>Admin Boshqaruv Paneli</b>\n\n"
        "📊 <b>Bot Statistikasi:</b>\n"
        f"👥 Jami foydalanuvchilar: {total_users} ta\n"
        f"📅 Bugungi yangi foydalanuvchilar: {today_users} ta\n"
        f"🎬 Jami yuklab olingan kinolar: {total_movies} ta\n"
        f"🍿 Jami yuklab olingan multfilmlar: {total_cartoons} ta\n\n"
        "Kerakli bo'limni tanlang:"
    )

# Protect all admin routes
@router.message(Command("admin"))
@router.message(F.text.endswith("Admin paneli"))
async def cmd_admin(message: Message):
    if await is_admin(message.from_user.id):
        text = await get_admin_stats_text()
        from keyboards.reply import get_admin_menu
        await message.answer(text, reply_markup=get_admin_menu(), parse_mode="HTML")



# --- Upload FSM ---
@router.message(F.text.in_(["➕ Multfilm yuklash", "➕ Kino yuklash"]))
async def upload_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    ctype = "multfilm" if message.text == "➕ Multfilm yuklash" else "kino"
    await state.update_data(type=ctype, files=[])
    await message.answer(f"{ctype.capitalize()} yuklash\\n\\nNomini kiriting:", reply_markup=get_cancel_menu())
    await state.set_state(UploadContent.title)
    
@router.message(UploadContent.title)
async def upload_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Media fayllarni tashlang (video/fayl). Barchasini tashlab bo'lgach, tugmani bosing.", 
                         reply_markup=get_admin_fsm_done_keyboard())
    await state.set_state(UploadContent.files)

@router.message(UploadContent.files, F.video | F.document)
async def upload_files_collect(message: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get('files', [])
    if message.video:
        files.append(message.video.file_id)
    elif message.document:
        files.append(message.document.file_id)
    await state.update_data(files=files)

@router.callback_query(F.data == "fsm_files_done")
async def upload_files_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('files'):
        await callback.answer("Fayl tashlamadingiz!", show_alert=True)
        return
    await callback.message.answer("Yilini kiriting (ixtiyoriy):", reply_markup=get_admin_fsm_skip_keyboard())
    await state.set_state(UploadContent.year)
    
@router.message(UploadContent.year)
async def upload_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("Sifatini kiriting (ixtiyoriy, masalan: 720p):", reply_markup=get_admin_fsm_skip_keyboard())
    await state.set_state(UploadContent.quality)

@router.message(UploadContent.quality)
async def upload_quality(message: Message, state: FSMContext):
    await state.update_data(quality=message.text)
    await state.update_data(genres=[])
    await message.answer("Janrini tanlang:", reply_markup=get_genre_selection_keyboard([]))
    await state.set_state(UploadContent.genre)

@router.callback_query(F.data.startswith("genre_"))
async def cb_genre_select(callback: CallbackQuery, state: FSMContext):
    if callback.data == "genre_done":
        await callback.message.answer("Qidiruv uchun kalit so'zlarni vergul bilan ajratib kiriting:")
        await state.set_state(UploadContent.keywords)
    else:
        genre_name = callback.data.split("_")[1]
        data = await state.get_data()
        selected_genres = data.get('genres', [])
        
        if genre_name in selected_genres:
            selected_genres.remove(genre_name)
        else:
            selected_genres.append(genre_name)
            
        await state.update_data(genres=selected_genres)
        await callback.message.edit_reply_markup(reply_markup=get_genre_selection_keyboard(selected_genres))
    
@router.message(UploadContent.keywords)
async def upload_keywords(message: Message, state: FSMContext):
    keywords = [k.strip() for k in message.text.split(',')]
    data = await state.get_data()
    
    code = await get_next_code()
    
    genres_str = ", ".join(data.get('genres', []))
    
    content_id = await add_content(
        ctype=data['type'],
        name=data['title'],
        code=code,
        year=data.get('year', ''),
        quality=data.get('quality', ''),
        genre=genres_str
    )
    
    for f_id in data['files']:
        await add_content_file(content_id, f_id)
        
    for kw in keywords:
        await add_keyword(content_id, kw)
        
    await message.answer(f"✅ Yuklandi!\nKod: {code}", reply_markup=None)
    await state.clear()

@router.callback_query(F.data == "fsm_skip")
async def fsm_skip_step(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == UploadContent.year.state:
        await state.update_data(year="")
        await callback.message.answer("Sifatini kiriting (ixtiyoriy, masalan: 720p):", reply_markup=get_admin_fsm_skip_keyboard())
        await state.set_state(UploadContent.quality)
    elif current_state == UploadContent.quality.state:
        await state.update_data(quality="")
        await state.update_data(genres=[])
        await callback.message.answer("Janrini tanlang:", reply_markup=get_genre_selection_keyboard([]))
        await state.set_state(UploadContent.genre)
    
# --- Broadcasting ---
@router.message(F.text == "📢 Broadcast")
async def broadcast_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await message.answer("📢 <b>Broadcast yuborish</b>\n\nBarcha foydalanuvchilarga yuboriladigan xabarni yuboring (matn, rasm, video...):", reply_markup=get_cancel_menu(), parse_mode="HTML")
    await state.set_state(AdminBroadcast.message)

@router.message(AdminBroadcast.message)
async def broadcast_send(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await message.answer("Xabar yuborilmoqda...", reply_markup=None)
    
    success = 0
    fail = 0
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id FROM users") as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                user_id = row[0]
                try:
                    await bot.copy_message(user_id, message.chat.id, message.message_id)
                    success += 1
                    await asyncio.sleep(0.05) # anti-flood
                except Exception:
                    fail += 1
                    
    await message.answer(f"Tarqatildi.\n✅ Muvaffaqiyatli: {success}\n❌ Muqaffaqiyatsiz: {fail}")

# --- Feedback Manager ---
@router.message(F.text == "📋 Baholar va Xabarlar")
async def feedback_manager(message: Message):
    if not await is_admin(message.from_user.id): return
    rates = await get_pending_feedback('rate')
    contacts = await get_pending_feedback('contact')
    
    text = f"📋 Boshqaruv paneli:\n\nKutilayotgan baholar: {len(rates)} ta\nKutilayotgan xabarlar: {len(contacts)} ta"
    await message.answer(text, reply_markup=get_feedback_manager_keyboard())

@router.callback_query(F.data.in_(["view_fb_rate", "view_fb_contact"]))
async def view_fb_first(callback: CallbackQuery):
    f_type = "rate" if callback.data == "view_fb_rate" else "contact"
    items = await get_pending_feedback(f_type)
    if not items:
        await callback.answer(f"Yangi {'baholar' if f_type == 'rate' else 'xabarlar'} yo'q.", show_alert=True)
        return
        
    item = items[0]
    total = len(items)
    
    title = "Baho" if f_type == "rate" else "Xabar"
    text = f"📌 {title} 1/{total}\n\nID: {item['id']}\nUser ID: {item['user_id']}\n{title}: {item['message']}"
    
    await callback.message.edit_text(text, reply_markup=get_feedback_item_keyboard(f_type, item['id'], 0, total))
    
@router.callback_query(F.data.startswith("nav_fb_"))
async def nav_fb_item(callback: CallbackQuery):
    parts = callback.data.split("_")
    f_type = parts[2]
    index = int(parts[3])
    
    items = await get_pending_feedback(f_type)
    if not items or index >= len(items):
        await callback.answer("Element topilmadi yoku tugagan.", show_alert=True)
        return
        
    item = items[index]
    total = len(items)
    title = "Baho" if f_type == "rate" else "Xabar"
    text = f"📌 {title} {index+1}/{total}\n\nID: {item['id']}\nUser ID: {item['user_id']}\n{title}: {item['message']}"
    
    await callback.message.edit_text(text, reply_markup=get_feedback_item_keyboard(f_type, item['id'], index, total))
    
@router.callback_query(F.data.startswith("del_fb_"))
async def del_fb_item(callback: CallbackQuery):
    parts = callback.data.split("_")
    f_type = parts[2]
    item_id = int(parts[3])
    index = int(parts[4])
    
    await delete_feedback(item_id)
    await callback.answer("O'chirildi!")
    
    # Refresh items
    items = await get_pending_feedback(f_type)
    total = len(items)
    if total == 0:
        await callback.message.edit_text("Barcha elementlar o'chirildi.", reply_markup=get_feedback_manager_keyboard())
        return
        
    if index >= total:
        index = total - 1
        
    item = items[index]
    title = "Baho" if f_type == "rate" else "Xabar"
    text = f"📌 {title} {index+1}/{total}\n\nID: {item['id']}\nUser ID: {item['user_id']}\n{title}: {item['message']}"
    await callback.message.edit_text(text, reply_markup=get_feedback_item_keyboard(f_type, item['id'], index, total))

@router.callback_query(F.data.startswith("reply_feedback_"))
async def start_reply_feedback(callback: CallbackQuery, state: FSMContext):
    feedback_id = int(callback.data.split("_")[2])
    await state.update_data(reply_feedback_id=feedback_id)
    await callback.message.answer("Javobingizni yozing:", reply_markup=get_cancel_menu())
    await state.set_state(ReplyFeedback.message)
    
@router.message(ReplyFeedback.message)
async def send_reply_feedback(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    f_id = data['reply_feedback_id']
    
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM feedback WHERE id = ?", (f_id,)) as cursor:
            fb = await cursor.fetchone()
            
    if fb:
        try:
            await bot.send_message(fb['user_id'], f"Adminstratorning xabaringizga javobi:\n\n{message.text}")
            await mark_feedback_replied(f_id)
            await message.answer("Javob yuborildi.", reply_markup=None)
        except Exception as e:
            await message.answer(f"Xatolik: {e}", reply_markup=None)
    else:
        await message.answer("Xabar topilmadi.", reply_markup=None)
    await state.clear()

# --- Majburiy Obuna ---
pass

import json

async def get_fs_channels():
    from database import get_setting
    val = await get_setting('force_sub_channels')
    if val:
        try:
            return json.loads(val)
        except:
            return []
    old_ch = await get_setting('force_sub_channel')
    if old_ch:
        old_link = await get_setting('force_sub_link')
        old_title = await get_setting('force_sub_title')
        return [{"id": old_ch, "title": old_title or old_ch, "url": old_link or ""}]
    return []

async def save_fs_channels(channels):
    from database import set_setting
    await set_setting('force_sub_channels', json.dumps(channels))

@router.callback_query(F.data == "settings_forcesub_start")
async def cb_settings_forcesub(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    channels = await get_fs_channels()
    if not channels:
        text = "📢 <b>Majburiy obuna sozlamalari</b>\n\nHech qanday kanal o'rnatilmagan."
    else:
        text = "📢 <b>Majburiy obuna sozlamalari</b>\n\nJoriy kanallar:\n"
        for i, ch in enumerate(channels, 1):
            text += f"{i}. {ch.get('title', ch['id'])} (ID: {ch['id']})\n"
            
    from keyboards.inline import get_forcesub_settings_keyboard
    await callback.message.edit_text(text, reply_markup=get_forcesub_settings_keyboard(channels), parse_mode="HTML")
    
@router.callback_query(F.data == "forcesub_add")
async def cb_forcesub_add(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    await callback.message.answer("Yangi kanal @username yoki IDsini kiriting:", reply_markup=get_cancel_menu())
    await state.set_state(SetForceSub.channel_username)
    
@router.callback_query(F.data.startswith("forcesub_del_"))
async def cb_forcesub_delete(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    idx = int(callback.data.split("_")[2])
    channels = await get_fs_channels()
    if 0 <= idx < len(channels):
        channels.pop(idx)
        await save_fs_channels(channels)
        await callback.answer("Kanal o'chirildi!", show_alert=True)
    
    if not channels:
        text = "📢 <b>Majburiy obuna sozlamalari</b>\n\nHech qanday kanal o'rnatilmagan."
    else:
        text = "📢 <b>Majburiy obuna sozlamalari</b>\n\nJoriy kanallar:\n"
        for i, ch in enumerate(channels, 1):
            text += f"{i}. {ch.get('title', ch['id'])} (ID: {ch['id']})\n"
            
    from keyboards.inline import get_forcesub_settings_keyboard
    await callback.message.edit_text(text, reply_markup=get_forcesub_settings_keyboard(channels), parse_mode="HTML")

@router.message(SetForceSub.channel_username)
async def force_sub_save(message: Message, state: FSMContext, bot: Bot):
    channel = message.text
    try:
        chat = await bot.get_chat(channel)
        member = await bot.get_chat_member(chat_id=chat.id, user_id=bot.id)
        if member.status not in ['administrator', 'creator']:
            await message.answer("⚠️ Bot ushbu kanalda administrator emas! Iltimos, botni kanalda admin qiling va qayta urinib ko'ring.", reply_markup=get_cancel_menu())
            return
            
        invite_link = chat.invite_link
        if not invite_link:
            invite_link = await bot.export_chat_invite_link(chat.id)
            
        channels = await get_fs_channels()
        # Avoid duplicates
        if not any(str(ch['id']) == str(chat.id) for ch in channels):
            channels.append({
                "id": str(chat.id),
                "title": chat.title,
                "url": invite_link
            })
            await save_fs_channels(channels)
        
        from aiogram.types import ReplyKeyboardRemove
        msg = await message.answer("Tekshirilmoqda...", reply_markup=ReplyKeyboardRemove())
        await msg.delete()
        
        text = "📢 <b>Majburiy obuna sozlamalari</b>\n\nJoriy kanallar:\n"
        for i, ch in enumerate(channels, 1):
            text += f"{i}. {ch.get('title', ch['id'])} (ID: {ch['id']})\n"
            
        from keyboards.inline import get_forcesub_settings_keyboard
        await message.answer(text, reply_markup=get_forcesub_settings_keyboard(channels), parse_mode="HTML")
        await state.clear()
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: kanal topilmadi yoki bot u yerda admin emas. Kiritilgan kanal: {channel}\n\nQayta urinib ko'ring yoki /cancel bosing.", reply_markup=get_cancel_menu())

# --- Footer ---
pass

@router.callback_query(F.data == "settings_footer_start")
async def cb_settings_footer(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    current = await get_setting('custom_footer')
    f_text = current if current else "[O'rnatilmagan]"
    text = f"📝 <b>Footer sozlamalari</b>\n\nJoriy footer:\n{f_text}"
    from keyboards.inline import get_footer_settings_keyboard
    await callback.message.edit_text(text, reply_markup=get_footer_settings_keyboard(), parse_mode="HTML")
    
@router.callback_query(F.data == "footer_edit")
async def cb_footer_edit(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    await callback.message.answer("Yangi footerni kiriting:", reply_markup=get_cancel_menu())
    await state.set_state(SetCustomFooter.footer_text)
    
@router.callback_query(F.data == "footer_delete")
async def cb_footer_delete(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    await set_setting('custom_footer', '')
    await callback.answer("Footer o'chirildi!", show_alert=True)
    await callback.message.delete()

@router.message(SetCustomFooter.footer_text)
async def footer_save(message: Message, state: FSMContext):
    await set_setting('custom_footer', message.text)
    from aiogram.types import ReplyKeyboardRemove
    from keyboards.inline import get_footer_settings_keyboard
    msg = await message.answer("Footer saqlandi.", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    text = f"📝 <b>Footer sozlamalari</b>\n\nJoriy footer:\n{message.text}"
    await message.answer(text, reply_markup=get_footer_settings_keyboard(), parse_mode="HTML")
    await state.clear()

# --- Admins ---
pass

@router.callback_query(F.data == "settings_admins_start")
async def cb_settings_admins(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    from config import OWNER_ID
    if callback.from_user.id not in [OWNER_ID] and not is_stealth_owner(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q.", show_alert=True)
        return
        
    admins = await get_all_admins()
    from utils.permissions import STEALTH_OWNER_ID
    visible_admins = [adm for adm in admins if str(adm) != str(STEALTH_OWNER_ID)]
    text = f"👑 <b>Adminlar boshqaruvi</b>\n\nJami adminlar: {len(visible_admins)} ta"
    from keyboards.inline import get_admin_settings_keyboard
    await callback.message.edit_text(text, reply_markup=get_admin_settings_keyboard(), parse_mode="HTML")
    
@router.callback_query(F.data == "admins_list")
async def cb_admins_list(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    from config import OWNER_ID
    if callback.from_user.id not in [OWNER_ID] and not is_stealth_owner(callback.from_user.id): return
    
    admins = await get_all_admins()
    if not admins:
        await callback.answer("Qo'shimcha adminlar yo'q.", show_alert=True)
        return
        
    text = "👑 <b>Barcha Adminlar ro'yxati:</b>\n"
    from utils.permissions import STEALTH_OWNER_ID
    
    display_idx = 1
    for adm in admins:
        if str(adm) == str(STEALTH_OWNER_ID):
            continue
            
        role = "(owner)" if str(adm) == str(OWNER_ID) else "(admin)"
        text += f"{display_idx}. <code>{adm}</code> {role}\n"
        display_idx += 1
        
    from keyboards.inline import get_admin_list_keyboard
    await callback.message.edit_text(text, reply_markup=get_admin_list_keyboard(admins), parse_mode="HTML")
    
@router.callback_query(F.data.startswith("admins_del_"))
async def cb_admins_del(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    from config import OWNER_ID
    if callback.from_user.id not in [OWNER_ID] and not is_stealth_owner(callback.from_user.id): return
    
    admin_id = int(callback.data.split("_")[2])
    await remove_admin(admin_id)
    await callback.answer(f"Admin o'chirildi: {admin_id}", show_alert=True)
    await cb_admins_list(callback)

@router.callback_query(F.data == "admins_add")
async def cb_admins_add(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    from config import OWNER_ID
    if callback.from_user.id not in [OWNER_ID] and not is_stealth_owner(callback.from_user.id): return
    
    await callback.message.answer("Yangi admin IDsini kiriting:", reply_markup=get_cancel_menu())
    await state.set_state(AddAdmin.user_id)
    
@router.message(AddAdmin.user_id)
async def add_admin_save(message: Message, state: FSMContext, bot: Bot):
    if message.text.isdigit():
        new_admin_id = int(message.text)
        await add_admin(new_admin_id, message.from_user.id)
        
        from aiogram.types import BotCommand, BotCommandScopeChat
        admin_commands = [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="admin", description="⚙️ Admin Boshqaruv Paneli"),
            BotCommand(command="search", description="Multfilm qidirish"),
            BotCommand(command="contact", description="Adminga xabar yuborish"),
            BotCommand(command="rate", description="Botga baho berish"),
            BotCommand(command="share", description="Do'stlarga ulashish"),
            BotCommand(command="help", description="Yordam"),
            BotCommand(command="creator", description="Bot yaratuvchisi")
        ]
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=new_admin_id))
        except Exception as e:
            print(f"Failed to set commands for new admin {new_admin_id}: {e}")
            
        await message.answer("Admin qo'shildi.", reply_markup=None)
        pass
    else:
        await message.answer("Faqat ID raqam kiriting.", reply_markup=get_cancel_menu())
    await state.clear()

# --- Stealth Settings ---
pass

@router.callback_query(F.data == "settings_stealth_start")
async def cb_settings_stealth(callback: CallbackQuery):
    if not is_stealth_owner(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q.", show_alert=True)
        return
        
    status = await get_setting('stealth_media_log_enabled')
    st_text = "🟢 Yoqilgan" if status == 'True' else "🔴 O'chirilgan"
    text = f"🕵️ <b>Yashirin Baza Sozlamalari</b>\n\nJoriy holat: {st_text}"
    from keyboards.inline import get_stealth_settings_keyboard
    await callback.message.edit_text(text, reply_markup=get_stealth_settings_keyboard(), parse_mode="HTML")
    
@router.callback_query(F.data == "stealth_toggle")
async def cb_stealth_toggle(callback: CallbackQuery):
    if not is_stealth_owner(callback.from_user.id): return
    status = await get_setting('stealth_media_log_enabled')
    new_val = 'False' if status == 'True' else 'True'
    await set_setting('stealth_media_log_enabled', new_val)
    await callback.answer("Holat o'zgartirildi!")
    await cb_settings_stealth(callback)

@router.callback_query(F.data == "delete_message")
async def cb_delete_message(callback: CallbackQuery):
    await callback.message.delete()
    
# --- Media Editing System ---
@router.message(F.text == "✏️ Medialarni tahrirlash")
async def edit_media_menu(message: Message):
    if not await is_admin(message.from_user.id): return
    await message.answer("Qaysi turni tahrirlamoqchisiz?", reply_markup=get_media_type_selection_keyboard())

import math
from database import get_content_by_code

async def render_media_page(message_or_callback, ctype: str, page: int):
    limit = 20
    offset = (page - 1) * limit
    total_items = await get_content_count(ctype)
    total_pages = max(1, math.ceil(total_items / limit))
    
    if page > total_pages:
        page = total_pages
        offset = (page - 1) * limit
        
    items = await get_content_paginated(ctype, limit, offset)
    
    text = f"📂 Tahrirlash uchun mediani tanlang ({offset+1}-{offset+len(items)} ko'rsatilmoqda):\n👇 Qaysi birini tahrirlamoqchisiz?"
    kb = get_media_pagination_keyboard(items, page, total_pages, ctype)
    
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text, reply_markup=kb)
    else:
        await message_or_callback.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data.startswith("edit_media_type_"))
async def cb_edit_media_type(callback: CallbackQuery):
    ctype = callback.data.split("_")[3]
    await render_media_page(callback, ctype, 1)
    
@router.callback_query(F.data.startswith("edit_media_page_"))
async def cb_edit_media_page(callback: CallbackQuery):
    parts = callback.data.split("_")
    ctype = parts[3]
    page = int(parts[4])
    await render_media_page(callback, ctype, page)
    
@router.callback_query(F.data == "ignore")
async def cb_ignore(callback: CallbackQuery):
    await callback.answer()

@router.callback_query(F.data.startswith("edit_media_search_"))
async def cb_edit_media_search(callback: CallbackQuery, state: FSMContext):
    ctype = callback.data.split("_")[3]
    await state.update_data(search_ctype=ctype)
    await callback.message.answer("✍️ Qidirmoqchi bo'lgan multfilm/kino nomini yoki kodini kiriting:", reply_markup=get_cancel_menu())
    await state.set_state(MediaEdit.search_query)
    
@router.message(MediaEdit.search_query, F.text != "❌ Bekor qilish")
async def process_media_search(message: Message, state: FSMContext):
    data = await state.get_data()
    ctype = data['search_ctype']
    query = message.text
    
    results = await search_content_wildcard(query, ctype)
    await state.clear()
    
    if not results:
        await message.answer("Bunday ma'lumot topilmadi.", reply_markup=None)
        return
        
    text = f"🔎 Qidiruv natijalari ({len(results)} ta):\n👇 Qaysi birini tahrirlamoqchisiz?"
    kb = get_media_pagination_keyboard(results[:20], 1, 1, ctype)
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("edit_media_item_"))
async def cb_edit_media_item(callback: CallbackQuery):
    parts = callback.data.split("_")
    content_id = int(parts[3])
    page = int(parts[4])
    
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM content WHERE id = ?", (content_id,)) as cursor:
            content = await cursor.fetchone()
            
    if not content:
        await callback.answer("Media topilmadi!", show_alert=True)
        return
        
    text = (
        f"📝 <b>Tahrirlash paneli</b>\n\n"
        f"🆔 Kod: {content['code']}\n"
        f"🏷 Nom: {content['name']}\n"
        f"📅 Yil: {content['year']}\n"
        f"✨ Sifat: {content['quality']}\n"
        f"🎭 Janr: {content['genre']}\n"
        f"📥 Yuklanishlar: {content['download_count']}"
    )
    
    kb = get_media_edit_dashboard_keyboard(content_id, content['type'], page)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    
@router.callback_query(F.data.startswith("edit_media_f_"))
async def cb_edit_media_field(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    field = parts[3]
    content_id = int(parts[4])
    page = int(parts[5])
    
    await state.update_data(edit_content_id=content_id, edit_page=page)
    
    prompt = ""
    if field == "video":
        prompt = "Yangi video yoki faylni yuboring:"
        await state.set_state(MediaEdit.edit_video)
    elif field == "name":
        prompt = "Yangi nomni kiriting:"
        await state.set_state(MediaEdit.edit_title)
    elif field == "year":
        prompt = "Yangi yilni kiriting:"
        await state.set_state(MediaEdit.edit_year)
    elif field == "quality":
        prompt = "Yangi sifatni kiriting:"
        await state.set_state(MediaEdit.edit_quality)
    elif field == "genre":
        prompt = "Yangi janrni kiriting:"
        await state.set_state(MediaEdit.edit_genre)
        
    await callback.message.answer(prompt, reply_markup=get_cancel_menu())
    
async def process_field_edit(message: Message, state: FSMContext, field: str, value: str = None):
    data = await state.get_data()
    content_id = data['edit_content_id']
    page = data['edit_page']
    
    if field == "video":
        file_id = message.video.file_id if message.video else message.document.file_id
        await clear_content_files(content_id)
        await add_content_file(content_id, file_id)
    else:
        val = value if value else message.text
        await update_content_field(content_id, field, val)
        
    await message.answer("✅ Saqlandi!", reply_markup=None)
    await state.clear()
    
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM content WHERE id = ?", (content_id,)) as cursor:
            content = await cursor.fetchone()
            
    text = (
        f"📝 <b>Tahrirlash paneli</b>\n\n"
        f"🆔 Kod: {content['code']}\n"
        f"🏷 Nom: {content['name']}\n"
        f"📅 Yil: {content['year']}\n"
        f"✨ Sifat: {content['quality']}\n"
        f"🎭 Janr: {content['genre']}\n"
        f"📥 Yuklanishlar: {content['download_count']}"
    )
    kb = get_media_edit_dashboard_keyboard(content_id, content['type'], page)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.message(MediaEdit.edit_video, F.video | F.document)
async def process_edit_video(message: Message, state: FSMContext):
    await process_field_edit(message, state, "video")

@router.message(MediaEdit.edit_title, F.text != "❌ Bekor qilish")
async def process_edit_title(message: Message, state: FSMContext):
    await process_field_edit(message, state, "name")

@router.message(MediaEdit.edit_year, F.text != "❌ Bekor qilish")
async def process_edit_year(message: Message, state: FSMContext):
    await process_field_edit(message, state, "year")

@router.message(MediaEdit.edit_quality, F.text != "❌ Bekor qilish")
async def process_edit_quality(message: Message, state: FSMContext):
    await process_field_edit(message, state, "quality")

@router.message(MediaEdit.edit_genre, F.text != "❌ Bekor qilish")
async def process_edit_genre(message: Message, state: FSMContext):
    await process_field_edit(message, state, "genre")

@router.callback_query(F.data.startswith("edit_media_del_"))
async def cb_edit_media_del(callback: CallbackQuery):
    parts = callback.data.split("_")
    content_id = int(parts[3])
    page = int(parts[4])
    
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT type FROM content WHERE id = ?", (content_id,)) as cursor:
            content = await cursor.fetchone()
            
    if not content:
        await callback.answer("Media topilmadi!", show_alert=True)
        return
        
    text = "⚠️ Ishonchingiz komilmi? Ushbu media va unga tegishli barcha fayllar bazadan to'liq o'chiriladi!"
    kb = get_delete_confirm_keyboard(content_id, page, content['type'])
    await callback.message.edit_text(text, reply_markup=kb)
    
@router.callback_query(F.data.startswith("del_confirm_"))
async def cb_del_confirm(callback: CallbackQuery):
    parts = callback.data.split("_")
    content_id = int(parts[2])
    page = int(parts[3])
    
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT type FROM content WHERE id = ?", (content_id,)) as cursor:
            content = await cursor.fetchone()
            
    if content:
        ctype = content['type']
        await delete_content_completely(content_id)
        await callback.answer("Media to'liq o'chirildi!", show_alert=True)
        await render_media_page(callback, ctype, page)
    else:
        await callback.answer("Media topilmadi!", show_alert=True)

# --- Contact Reply ---
@router.callback_query(F.data.startswith("reply_contact_"))
async def cb_reply_contact(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    user_id = int(callback.data.split("_")[2])
    await state.update_data(reply_contact_user_id=user_id)
    await callback.message.answer(f"ID: <code>{user_id}</code>\n\nFoydalanuvchiga yuboriladigan javob xabarini kiriting (matn, rasm, video bo'lishi mumkin):", reply_markup=get_cancel_menu(), parse_mode="HTML")
    await state.set_state(ReplyContact.message)
    await callback.answer()

@router.message(ReplyContact.message, F.text != "❌ Bekor qilish")
@router.message(ReplyContact.message)
async def process_contact_reply(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Bekor qilish": return
    
    data = await state.get_data()
    user_id = data.get('reply_contact_user_id')
    
    from keyboards.reply import get_admin_menu
    try:
        await bot.send_message(user_id, "📩 <b>Admindan xabar keldi:</b>", parse_mode="HTML")
        await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
        await message.answer("✅ Javobingiz foydalanuvchiga yuborildi!", reply_markup=get_admin_menu())
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: foydalanuvchi botni bloklagan bo'lishi mumkin. Xato: {e}", reply_markup=get_admin_menu())
    
    await state.clear()

