from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from aiogram.exceptions import TelegramBadRequest
from database import get_setting
from keyboards.inline import get_force_sub_keyboard
from utils.permissions import is_admin

class ForceSubMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        # Check if it's a message or callback
        user = None
        is_callback = False
        
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            is_callback = True
            
        if not user:
            return await handler(event, data)
            
        # Exclude admins from force sub
        if await is_admin(user.id):
            return await handler(event, data)
            
        channel_id_or_username = await get_setting('force_sub_channel')
        if not channel_id_or_username:
            return await handler(event, data)
            
        bot = data['bot']
        try:
            member = await bot.get_chat_member(chat_id=channel_id_or_username, user_id=user.id)
            if member.status in ['member', 'administrator', 'creator']:
                return await handler(event, data)
        except Exception as e:
            print(f"Force sub error: {e}")
            # If we can't check (bot not admin, channel deleted, etc), bypass to avoid locking users out.
            return await handler(event, data)
            
        # Determine channel link to show user
        channel_link = channel_id_or_username
        if not channel_link.startswith('http'):
            if channel_link.startswith('@'):
                channel_link = f"https://t.me/{channel_link[1:]}"
            else:
                try:
                    chat = await bot.get_chat(channel_id_or_username)
                    if chat.invite_link:
                        channel_link = chat.invite_link
                    else:
                        channel_link = await bot.export_chat_invite_link(channel_id_or_username)
                except Exception as e:
                    print(f"Cannot get invite link: {e}")
                    return await handler(event, data)
                
        text = "Botdan foydalanish uchun quyidagi kanalga obuna bo'lishingiz kerak."
        kb = get_force_sub_keyboard(channel_link)
        
        if is_callback:
            if event.data == "check_sub":
                await event.answer("Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)
            else:
                await bot.send_message(chat_id=user.id, text=text, reply_markup=kb)
        else:
            await event.answer(text, reply_markup=kb)
        
        return
