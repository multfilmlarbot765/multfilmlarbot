import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db, ping_db, close_db
from handlers import user, admin
from middlewares.forcesub import ForceSubMiddleware

async def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN is not set in .env")
        return
        
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.message.middleware(ForceSubMiddleware())
    dp.callback_query.middleware(ForceSubMiddleware())
    
    dp.include_router(admin.router)
    dp.include_router(user.router)
    
    from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="search", description="Multfilm qidirish"),
        BotCommand(command="contact", description="Adminga xabar yuborish"),
        BotCommand(command="rate", description="Botga baho berish"),
        BotCommand(command="share", description="Do'stlarga ulashish"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="creator", description="Bot yaratuvchisi")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    
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
    
    from database import get_all_admins
    all_admins = await get_all_admins()
    for admin_id in all_admins:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception as e:
            print(f"Failed to set commands for admin {admin_id}: {e}")
            
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Ping database to verify connection
    await ping_db()
    
    print("Bot is starting...")
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
