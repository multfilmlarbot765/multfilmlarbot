import re
with open('handlers/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('f"{ctype.capitalize()} yuklash\n\nNomini kiriting:"', 'f"{ctype.capitalize()} yuklash\\n\\nNomini kiriting:"')
text = text.replace('"📢 **Broadcast yuborish**\n\nBarcha foydalanuvchilarga yuboriladigan xabarni yuboring (matn, rasm, video...):"', '"📢 **Broadcast yuborish**\\n\\nBarcha foydalanuvchilarga yuboriladigan xabarni yuboring (matn, rasm, video...):"')
text = text.replace('f"📋 **Baholar va Xabarlar boshqaruv paneli**\n\n⭐ Yangi baholar: {c1} ta\n📩 Yangi xabarlar: {c2} ta"', 'f"📋 **Baholar va Xabarlar boshqaruv paneli**\\n\\n⭐ Yangi baholar: {c1} ta\\n📩 Yangi xabarlar: {c2} ta"')
with open('handlers/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)
