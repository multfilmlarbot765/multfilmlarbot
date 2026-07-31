import re

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple replace
    new_content = content.replace('parse_mode="Markdown"', 'parse_mode="HTML"')
    
    # Replace **bold** with <b>bold</b> ONLY if parse_mode is HTML now
    new_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', new_content)
    
    if content != new_content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {filename}')
    else:
        print(f'No changes needed in {filename}')

process_file('handlers/admin.py')
process_file('handlers/user.py')
