import re

with open('handlers/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update cmd_admin and cb_admin_panel_open to send inline keyboard
text = re.sub(
    r'@router\.message\(Command\("admin"\)\)\nasync def cmd_admin\(message: Message\):.*?@router\.callback_query',
    '''@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if await is_admin(message.from_user.id):
        from aiogram.types import ReplyKeyboardRemove
        msg = await message.answer("Admin paneli ochilmoqda...", reply_markup=ReplyKeyboardRemove())
        await msg.delete()
        text = await get_admin_stats_text()
        from keyboards.inline import get_admin_panel_keyboard
        await message.answer(text, reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")

@router.callback_query''', text, flags=re.DOTALL
)

text = re.sub(
    r'@router\.callback_query\(F\.data == "admin_panel_open"\)\nasync def cb_admin_panel_open\(callback: CallbackQuery\):.*?@router\.message',
    '''@router.callback_query(F.data == "admin_panel_open")
async def cb_admin_panel_open(callback: CallbackQuery):
    if await is_admin(callback.from_user.id):
        text = await get_admin_stats_text()
        from keyboards.inline import get_admin_panel_keyboard
        await callback.message.edit_text(text, reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.message''', text, flags=re.DOTALL, count=1
)

# 2. Refactor Upload
text = re.sub(
    r'@router\.message\(F\.text\.in_\(\["➕ Multfilm yuklash", "➕ Kino yuklash"\]\)\)\nasync def upload_start\(message: Message, state: FSMContext\):\n    if not await is_admin\(message\.from_user\.id\): return\n    ctype = "multfilm" if message\.text == "➕ Multfilm yuklash" else "kino"\n    await state\.update_data\(type=ctype, files=\[\]\)\n    await message\.answer\("Nomini kiriting:", reply_markup=get_cancel_menu\(\)\)\n    await state\.set_state\(UploadContent\.title\)',
    '''@router.callback_query(F.data.in_(["admin_upload_multfilm", "admin_upload_kino"]))
async def upload_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    ctype = "multfilm" if callback.data == "admin_upload_multfilm" else "kino"
    await state.update_data(type=ctype, files=[])
    await callback.message.edit_text(f"{ctype.capitalize()} yuklash\\n\\nNomini kiriting:")
    await state.set_state(UploadContent.title)
    await callback.answer()''', text
)

# 3. Refactor Broadcast
text = re.sub(
    r'@router\.message\(F\.text == "📢 Xabar yuborish \(Broadcast\)"\)\nasync def broadcast_start\(message: Message, state: FSMContext\):\n    if not await is_admin\(message\.from_user\.id\): return\n    await message\.answer\("Barcha foydalanuvchilarga yuboriladigan xabarni kiriting \(matn, rasm, video...\):", reply_markup=get_cancel_menu\(\)\)\n    await state\.set_state\(AdminBroadcast\.message\)',
    '''@router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    await callback.message.edit_text("📢 **Broadcast yuborish**\\n\\nBarcha foydalanuvchilarga yuboriladigan xabarni yuboring (matn, rasm, video...):", parse_mode="Markdown")
    await state.set_state(AdminBroadcast.message)
    await callback.answer()''', text
)

# 4. Refactor Feedback panel
text = re.sub(
    r'@router\.message\(F\.text == "📋 Baholar va Xabarlar boshqaruv paneli"\)\nasync def feedback_manager\(message: Message\):\n    if not await is_admin\(message\.from_user\.id\): return\n    \n    c1, c2 = await get_pending_feedback\(\)\n    text = f"📋 \*\*Baholar va Xabarlar boshqaruv paneli\*\*\n\n⭐ Yangi baholar: {c1} ta\n📩 Yangi xabarlar: {c2} ta"\n    \n    await message\.answer\(text, reply_markup=get_feedback_manager_keyboard\(\), parse_mode="Markdown"\)',
    '''@router.callback_query(F.data == "admin_feedback_panel")
async def feedback_manager(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    
    c1, c2 = await get_pending_feedback()
    text = f"📋 **Baholar va Xabarlar boshqaruv paneli**\\n\\n⭐ Yangi baholar: {c1} ta\\n📩 Yangi xabarlar: {c2} ta"
    
    await callback.message.edit_text(text, reply_markup=get_feedback_manager_keyboard(), parse_mode="Markdown")
    await callback.answer()''', text
)

# 5. Refactor Edit Media panel
text = re.sub(
    r'@router\.message\(F\.text == "✏️ Medialarni tahrirlash"\)\nasync def edit_media_menu\(message: Message, state: FSMContext\):\n    if not await is_admin\(message\.from_user\.id\): return\n    await state\.clear\(\)\n    await message\.answer\("Tahrirlash uchun media turini tanlang:", reply_markup=get_media_type_selection_keyboard\(\)\)',
    '''@router.callback_query(F.data == "admin_edit_media")
async def edit_media_menu(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    await state.clear()
    await callback.message.edit_text("Tahrirlash uchun media turini tanlang:", reply_markup=get_media_type_selection_keyboard())
    await callback.answer()''', text
)

# 6. Remove the 4 settings message handlers and replace them with pass, since the new callback handlers will do the job.
# Actually, the user says "Clicking ANY sub-menu button MUST update the existing message", and our callback handlers from before edit the message!
# Wait, I had changed the callbacks to message handlers. Let me change them back!
text = re.sub(r'@router\.message\(F\.text == "⚙️ Majburiy obuna sozlash"\)\nasync def settings_forcesub_start\(message: Message\):.*?await message\.answer\(text, reply_markup=get_forcesub_settings_keyboard\(\), parse_mode="Markdown"\)', 'pass', text, flags=re.DOTALL)
text = re.sub(r'@router\.message\(F\.text == "📝 Footer sozlash"\)\nasync def settings_footer_start\(message: Message\):.*?await message\.answer\(text, reply_markup=get_footer_settings_keyboard\(\), parse_mode="Markdown"\)', 'pass', text, flags=re.DOTALL)
text = re.sub(r'@router\.message\(F\.text == "👑 Adminlar boshqaruvi"\)\nasync def settings_admins_start\(message: Message\):.*?await message\.answer\(text, reply_markup=get_admin_settings_keyboard\(\), parse_mode="Markdown"\)', 'pass', text, flags=re.DOTALL)
text = re.sub(r'@router\.message\(F\.text == "⚙️ Baza Sozlamalari"\)\nasync def settings_stealth_start\(message: Message\):.*?await message\.answer\(text, reply_markup=get_stealth_settings_keyboard\(\), parse_mode="Markdown"\)', 'pass', text, flags=re.DOTALL)


# Now wait, we need to make sure the callback queries like cb_settings_forcesub are mapped to settings_forcesub_start callback data (because I used that in the new inline keyboard!)
text = text.replace('@router.callback_query(F.data == "settings_forcesub")', '@router.callback_query(F.data == "settings_forcesub_start")')
text = text.replace('@router.callback_query(F.data == "settings_footer")', '@router.callback_query(F.data == "settings_footer_start")')
text = text.replace('@router.callback_query(F.data == "settings_admins")', '@router.callback_query(F.data == "settings_admins_start")')
text = text.replace('@router.callback_query(F.data == "settings_stealth")', '@router.callback_query(F.data == "settings_stealth_start")')

with open('handlers/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)
