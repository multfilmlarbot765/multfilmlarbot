import re
with open('handlers/user.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the specific multi-line f-string that's broken in cb_check_forcesub
old_broken_string = r'greeting = f"👋 Assalomu alaykum \{callback.from_user.full_name\} botimizga xush kelibsiz\.\n\n✍🏻 Multfilm kodini yuboring\."'
new_string = 'greeting = f"👋 Assalomu alaykum {callback.from_user.full_name} botimizga xush kelibsiz.\\n\\n✍🏻 Multfilm kodini yuboring."'

text = re.sub(old_broken_string, new_string, text)

with open('handlers/user.py', 'w', encoding='utf-8') as f:
    f.write(text)
