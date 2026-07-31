from typing import Any, Awaitable, Callable, Dict
import json
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import get_setting
from utils.permissions import is_admin, is_stealth_owner
from config import OWNER_ID

class ForceSubMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        is_callback = False
        
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            is_callback = True
            # Allow the check_forcesub callback itself to pass through so the handler can evaluate it
            if event.data == "check_forcesub":
                return await handler(event, data)
                
        if not user:
            return await handler(event, data)
            
        # 1. Exemptions: OWNER, STEALTH_OWNER, DB Admins
        if user.id == OWNER_ID or is_stealth_owner(user.id) or await is_admin(user.id):
            return await handler(event, data)
            
        # 2. Fetch channel config
        channels_json = await get_setting('force_sub_channels')
        channels = []
        if channels_json:
            try:
                channels = json.loads(channels_json)
            except Exception:
                pass
        else:
            old_ch = await get_setting('force_sub_channel')
            if old_ch:
                old_link = await get_setting('force_sub_link')
                old_title = await get_setting('force_sub_title')
                channels = [{"id": old_ch, "title": old_title or old_ch, "url": old_link or "https://t.me/telegram"}]
                
        if not channels:
            return await handler(event, data)
            
        bot = data['bot']
        
        try:
            # 3. Check membership
            must_join = []
            for ch in channels:
                try:
                    member = await bot.get_chat_member(chat_id=ch['id'], user_id=user.id)
                    if member.status in ['left', 'kicked']:
                        must_join.append(ch)
                except Exception as e:
                    print(f"Force sub check error for {ch['id']}: {e}")
                    # If error (e.g. bot not admin), we skip checking this channel (fail open)
                    pass
            
            if must_join:
                # Block handler and send force sub prompt
                text = "⚠️ Botdan foydalanish uchun quyidagi kanal(lar)ga obuna bo'lishingiz shart!"
                
                inline_keyboard = []
                for ch in must_join:
                    inline_keyboard.append([InlineKeyboardButton(text=f"📢 {ch.get('title', 'Kanal')}", url=ch.get('url', 'https://t.me/telegram'))])
                
                inline_keyboard.append([InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_forcesub")])
                
                kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
                
                if is_callback:
                    await event.message.answer(text, reply_markup=kb)
                    await event.answer()
                else:
                    await event.answer(text, reply_markup=kb)
                
                # Block the handler execution
                return
                
        except Exception as e:
            print(f"Force sub general error: {e}")
            return await handler(event, data)
            
        # If member or restricted etc (not left/kicked)
        return await handler(event, data)
