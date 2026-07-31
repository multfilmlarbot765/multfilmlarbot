from typing import Any, Awaitable, Callable, Dict
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
        channel_id_str = await get_setting('force_sub_channel')
        if not channel_id_str:
            return await handler(event, data)
            
        invite_link = await get_setting('force_sub_link')
        if not invite_link:
            invite_link = "https://t.me/telegram"
            
        bot = data['bot']
        
        try:
            # 3. Check membership
            member = await bot.get_chat_member(chat_id=channel_id_str, user_id=user.id)
            if member.status in ['left', 'kicked']:
                # Block handler and send force sub prompt
                text = "⚠️ Botdan foydalanish uchun quyidagi kanalimizga obuna bo'lishingiz shart!"
                
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=invite_link)],
                        [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_forcesub")]
                    ]
                )
                
                if is_callback:
                    await event.message.answer(text, reply_markup=kb)
                    await event.answer()
                else:
                    await event.answer(text, reply_markup=kb)
                
                # Block the handler execution
                return
                
        except Exception as e:
            print(f"Force sub check error: {e}")
            # On API error (e.g., bot lost admin), fail open
            return await handler(event, data)
            
        # If member or restricted etc (not left/kicked)
        return await handler(event, data)
