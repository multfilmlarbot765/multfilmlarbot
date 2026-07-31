import re
with open('handlers/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Refactor force_sub_save
old_fss = r'''@router\.message\(SetForceSub\.channel_username\)\nasync def force_sub_save\(message: Message, state: FSMContext\):\n    await set_setting\('force_sub_channel', message\.text\)\n    await message\.answer\("Majburiy obuna saqlandi\.", reply_markup=None\)\n    await state\.clear\(\)\n    pass'''

new_fss = '''@router.message(SetForceSub.channel_username)
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
            
        await set_setting('force_sub_channel', str(chat.id))
        await set_setting('force_sub_link', invite_link)
        await set_setting('force_sub_title', chat.title)
        
        from aiogram.types import ReplyKeyboardRemove
        msg = await message.answer("Tekshirilmoqda...", reply_markup=ReplyKeyboardRemove())
        await msg.delete()
        
        from keyboards.inline import get_forcesub_settings_keyboard
        text = f"📢 **Majburiy obuna sozlamalari**\\n\\nJoriy kanal: {chat.title}\\nID: {chat.id}"
        await message.answer(text, reply_markup=get_forcesub_settings_keyboard(), parse_mode="Markdown")
        await state.clear()
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: kanal topilmadi yoki bot u yerda admin emas. Kiritilgan kanal: {channel}\\n\\nQayta urinib ko'ring yoki /cancel bosing.", reply_markup=get_cancel_menu())'''

text = re.sub(old_fss, new_fss, text, flags=re.DOTALL)

# Let's fix admin cancel handler which also used get_admin_menu
old_cancel = r'''@router\.message\(F\.text == "❌ Bekor qilish"\)\nasync def admin_cancel_handler\(message: Message, state: FSMContext\):\n    await state\.clear\(\)\n    text = await get_admin_stats_text\(\)\n    await message\.answer\("Amal bekor qilindi\.\\n\\n" \+ text, reply_markup=None, parse_mode="Markdown"\)'''
new_cancel = '''@router.message(F.text == "❌ Bekor qilish")
async def admin_cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    from aiogram.types import ReplyKeyboardRemove
    from keyboards.inline import get_admin_panel_keyboard
    msg = await message.answer("Amal bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    text = await get_admin_stats_text()
    await message.answer(text, reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")'''

text = re.sub(old_cancel, new_cancel, text, flags=re.DOTALL)

# Same for footer_save
old_footer = r'''@router\.message\(SetCustomFooter\.footer_text\)\nasync def footer_save\(message: Message, state: FSMContext\):\n    await set_setting\('custom_footer', message\.text\)\n    await message\.answer\("Footer saqlandi\.", reply_markup=None\)\n    await state\.clear\(\)\n    pass'''
new_footer = '''@router.message(SetCustomFooter.footer_text)
async def footer_save(message: Message, state: FSMContext):
    await set_setting('custom_footer', message.text)
    from aiogram.types import ReplyKeyboardRemove
    from keyboards.inline import get_footer_settings_keyboard
    msg = await message.answer("Footer saqlandi.", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    text = f"📝 **Footer sozlamalari**\\n\\nJoriy footer:\\n{message.text}"
    await message.answer(text, reply_markup=get_footer_settings_keyboard(), parse_mode="Markdown")
    await state.clear()'''

text = re.sub(old_footer, new_footer, text, flags=re.DOTALL)


# Same for add_admin_save
old_add_admin = r'''@router\.message\(AddAdmin\.user_id\)\nasync def add_admin_save\(message: Message, state: FSMContext, bot: Bot\):\n    new_admin_id = message\.text\.strip\(\)\n    if new_admin_id\.isdigit\(\):\n        new_admin_id = int\(new_admin_id\)\n        await add_admin\(new_admin_id\)\n        \n        # Set admin commands for the new admin\n        from aiogram\.types import BotCommand, BotCommandScopeChat\n        admin_commands = \[\n            BotCommand\(command="start", description="Botni ishga tushirish"\),\n            BotCommand\(command="admin", description="Admin panel"\),\n            BotCommand\(command="help", description="Yordam"\),\n            BotCommand\(command="creator", description="Bot yaratuvchisi"\)\n        \]\n        try:\n            await bot\.set_my_commands\(admin_commands, scope=BotCommandScopeChat\(chat_id=new_admin_id\)\)\n        except Exception as e:\n            print\(f"Failed to set commands for new admin {new_admin_id}: {e}"\)\n            \n        await message\.answer\("Admin qo'shildi\.", reply_markup=None\)\n        pass\n    else:\n        await message\.answer\("Faqat ID raqam kiriting\.", reply_markup=get_cancel_menu\(\)\)\n    await state\.clear\(\)'''

new_add_admin = '''@router.message(AddAdmin.user_id)
async def add_admin_save(message: Message, state: FSMContext, bot: Bot):
    new_admin_id = message.text.strip()
    if new_admin_id.isdigit():
        new_admin_id = int(new_admin_id)
        await add_admin(new_admin_id)
        
        # Set admin commands for the new admin
        from aiogram.types import BotCommand, BotCommandScopeChat
        admin_commands = [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="admin", description="Admin panel"),
            BotCommand(command="help", description="Yordam"),
            BotCommand(command="creator", description="Bot yaratuvchisi")
        ]
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=new_admin_id))
        except Exception as e:
            print(f"Failed to set commands for new admin {new_admin_id}: {e}")
            
        from aiogram.types import ReplyKeyboardRemove
        from keyboards.inline import get_admin_settings_keyboard
        msg = await message.answer("Admin qo'shildi.", reply_markup=ReplyKeyboardRemove())
        await msg.delete()
        
        admins = await get_admins()
        text = f"👑 **Adminlar boshqaruvi**\\n\\nJami adminlar: {len(admins)} ta"
        await message.answer(text, reply_markup=get_admin_settings_keyboard(), parse_mode="Markdown")
        await state.clear()
    else:
        await message.answer("Faqat ID raqam kiriting.", reply_markup=get_cancel_menu())
        await state.clear()'''

text = re.sub(old_add_admin, new_add_admin, text, flags=re.DOTALL)

with open('handlers/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)
