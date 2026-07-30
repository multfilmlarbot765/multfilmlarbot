import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from config import DATABASE_CHANNEL_ID
from database import get_setting, get_content_by_code, get_files_by_content_id

async def log_new_user(bot: Bot, user_id: int, name: str, username: str):
    if not DATABASE_CHANNEL_ID:
        return
    
    uname_str = f"@{username}" if username else "Mavjud emas"
    msg = f"🆕 Yangi foydalanuvchi!\n\nID: {user_id}\nIsm: {name}\nUsername: {uname_str}"
    
    try:
        await bot.send_message(DATABASE_CHANNEL_ID, msg)
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await bot.send_message(DATABASE_CHANNEL_ID, msg)
    except Exception as e:
        print(f"Error logging new user: {e}")

async def log_media_download(bot: Bot, user_id: int, name: str, username: str, content_name: str, code: int):
    if not DATABASE_CHANNEL_ID:
        return
        
    stealth_log = await get_setting('stealth_media_log_enabled')
    if stealth_log != 'True':
        return
        
    content = await get_content_by_code(code)
    if not content:
        return
        
    file_ids = await get_files_by_content_id(content['id'])
    if not file_ids:
        return
        
    uname_str = username if username else "Mavjud emas"
    
    caption = (
        f"📥 Media yuklandi!\n"
        f"👤 Ism: {name}\n"
        f"🔗 Username: @{uname_str}\n"
        f"🆔 ID: <code>{user_id}</code>\n\n"
        f"🎬 Kontent: {content_name} | Kod: {code}"
    )
    
    # Send the first file with the caption
    for i, f_id in enumerate(file_ids):
        current_caption = caption if i == 0 else ""
        try:
            await bot.send_document(DATABASE_CHANNEL_ID, f_id, caption=current_caption, parse_mode="HTML")
        except Exception:
            try:
                await bot.send_video(DATABASE_CHANNEL_ID, f_id, caption=current_caption, parse_mode="HTML")
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                await bot.send_video(DATABASE_CHANNEL_ID, f_id, caption=current_caption, parse_mode="HTML")
            except Exception as ex:
                print(f"Error sending file in log: {ex}")

async def log_rating(bot: Bot, user_id: int, name: str, username: str, stars: int):
    if not DATABASE_CHANNEL_ID:
        return
        
    uname_str = username if username else "Mavjud emas"
    
    msg = (
        f"⭐ **Yangi Baho Qoldirildi!**\n"
        f"👤 Ism: {name}\n"
        f"🔗 Username: @{uname_str}\n"
        f"🆔 ID: <code>{user_id}</code>\n\n"
        f"🌟 Baho: {stars}/5"
    )
    
    try:
        await bot.send_message(DATABASE_CHANNEL_ID, msg, parse_mode="HTML")
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await bot.send_message(DATABASE_CHANNEL_ID, msg, parse_mode="HTML")
    except Exception as e:
        print(f"Error logging rating: {e}")

async def log_contact(bot: Bot, user_id: int, name: str, username: str, message_text: str):
    if not DATABASE_CHANNEL_ID:
        return
        
    uname_str = username if username else "Mavjud emas"
    
    msg = (
        f"📩 **Yangi Murojaat!**\n"
        f"👤 Ism: {name}\n"
        f"🔗 Username: @{uname_str}\n"
        f"🆔 ID: <code>{user_id}</code>\n\n"
        f"💬 Xabar: {message_text}"
    )
    
    try:
        await bot.send_message(DATABASE_CHANNEL_ID, msg, parse_mode="HTML")
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await bot.send_message(DATABASE_CHANNEL_ID, msg, parse_mode="HTML")
    except Exception as e:
        print(f"Error logging contact: {e}")
