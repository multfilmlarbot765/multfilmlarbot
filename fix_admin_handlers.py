import re
with open('handlers/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix get_admins import
text = text.replace('get_total_movie_downloads, get_total_cartoon_downloads)', 'get_total_movie_downloads, get_total_cartoon_downloads, get_all_admins)')

# Fix get_admins call
text = text.replace('admins = await get_admins()', 'admins = await get_all_admins()')

# Fix upload_start callback reference
old_upload = r'await callback\.message\.edit_text\(f"\{ctype\.capitalize\(\)\} yuklash\\\\n\\\\nNomini kiriting:"\)'
new_upload = 'await message.answer(f"{ctype.capitalize()} yuklash\\n\\nNomini kiriting:", reply_markup=get_cancel_menu())'
text = re.sub(old_upload, new_upload, text)

# Just to be safe, if the previous string replacement had single \n instead of double \\n
old_upload_2 = r'await callback\.message\.edit_text\(f"\{ctype\.capitalize\(\)\} yuklash\\n\\nNomini kiriting:"\)'
text = re.sub(old_upload_2, new_upload, text)


# Fix broadcast text
text = text.replace('@router.message(F.text == "📢 Xabar yuborish (Broadcast)")', '@router.message(F.text == "📢 Broadcast")')

# Fix feedback manager text
text = text.replace('@router.message(F.text == "📋 Baholar va Xabarlar boshqaruv paneli")', '@router.message(F.text == "📋 Baholar va Xabarlar")')

with open('handlers/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)
