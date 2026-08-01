import aiosqlite
import asyncio

DB_NAME = 'bot_database.sqlite'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY,
                added_by INTEGER
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                name TEXT,
                code INTEGER UNIQUE,
                year TEXT,
                quality TEXT,
                genre TEXT,
                download_count INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS content_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                file_id TEXT,
                FOREIGN KEY(content_id) REFERENCES content(id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                keyword TEXT,
                FOREIGN KEY(content_id) REFERENCES content(id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                message TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Default settings
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('stealth_media_log_enabled', 'True')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('custom_footer', '')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('force_sub_channel', '')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('movies_channel_link', '')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('main_channel_url', 'https://t.me/multifilmlarobot')")
        await db.commit()

# --- Users ---
async def add_user(user_id: int, name: str, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            
        if user:
            await db.execute("UPDATE users SET name = ?, username = ? WHERE id = ?", (name, username, user_id))
            await db.commit()
            return False # Not new
        else:
            await db.execute("INSERT INTO users (id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
            await db.commit()
            return True # Is new

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

# --- Admins ---
async def get_admins():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id FROM admins") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def get_all_admins():
    from config import OWNER_ID
    from utils.permissions import STEALTH_OWNER_ID
    admins = await get_admins()
    all_admins = set(admins)
    if OWNER_ID:
        all_admins.add(int(OWNER_ID))
    all_admins.add(STEALTH_OWNER_ID)
    return list(all_admins)

async def add_admin(user_id: int, added_by: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO admins (id, added_by) VALUES (?, ?)", (user_id, added_by))
        await db.commit()

async def remove_admin(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM admins WHERE id = ?", (user_id,))
        await db.commit()

# --- Content ---
async def add_content(ctype: str, name: str, code: int, year: str, quality: str, genre: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO content (type, name, code, year, quality, genre) VALUES (?, ?, ?, ?, ?, ?)",
            (ctype, name, code, year, quality, genre)
        )
        await db.commit()
        async with db.execute("SELECT last_insert_rowid()") as cursor:
            return (await cursor.fetchone())[0]

async def add_content_file(content_id: int, file_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO content_files (content_id, file_id) VALUES (?, ?)", (content_id, file_id))
        await db.commit()

async def add_keyword(content_id: int, keyword: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO keywords (content_id, keyword) VALUES (?, ?)", (content_id, keyword.lower().strip()))
        await db.commit()

async def get_content_by_code(code: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM content WHERE code = ?", (code,)) as cursor:
            return await cursor.fetchone()

async def get_files_by_content_id(content_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT file_id FROM content_files WHERE content_id = ?", (content_id,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def increment_download(content_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE content SET download_count = download_count + 1 WHERE id = ?", (content_id,))
        await db.commit()

async def search_content_by_keyword(keyword: str):
    keyword_clean = keyword.lower().strip()
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT DISTINCT c.* FROM content c
            LEFT JOIN keywords k ON c.id = k.content_id
            WHERE LOWER(c.name) LIKE ? OR LOWER(k.keyword) LIKE ?
        """
        like_kw = f"%{keyword_clean}%"
        async with db.execute(query, (like_kw, like_kw)) as cursor:
            return await cursor.fetchall()

async def get_top_content(limit: int = 10):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM content ORDER BY download_count DESC LIMIT ?", (limit,)) as cursor:
            return await cursor.fetchall()

async def get_random_content():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM content ORDER BY RANDOM() LIMIT 1") as cursor:
            return await cursor.fetchone()

async def get_next_code():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT MAX(code) FROM content") as cursor:
            row = await cursor.fetchone()
            return (row[0] or 1000) + 1

# --- Statistics ---
async def get_total_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_today_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE DATE(joined_date) = DATE('now')") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_total_movie_downloads():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COALESCE(SUM(download_count), 0) FROM content WHERE type = 'kino'") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_total_cartoon_downloads():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COALESCE(SUM(download_count), 0) FROM content WHERE type = 'multfilm'") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

# --- Settings ---
async def get_setting(key: str):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()

# --- Feedback ---
async def add_feedback(user_id: int, f_type: str, message: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO feedback (user_id, type, message) VALUES (?, ?, ?)", (user_id, f_type, message))
        await db.commit()

async def get_pending_feedback(f_type: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM feedback WHERE type = ? AND status = 'pending' ORDER BY id ASC", (f_type,)) as cursor:
            return await cursor.fetchall()

async def mark_feedback_replied(feedback_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE feedback SET status = 'replied' WHERE id = ?", (feedback_id,))
        await db.commit()

async def delete_feedback(feedback_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
        await db.commit()

# --- Media Editing & Pagination ---
async def get_content_count(ctype: str):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM content WHERE type = ?", (ctype,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_content_paginated(ctype: str, limit: int, offset: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM content WHERE type = ? ORDER BY id DESC LIMIT ? OFFSET ?", (ctype, limit, offset)) as cursor:
            return await cursor.fetchall()

async def search_content_wildcard(query: str, ctype: str):
    query_clean = query.lower().strip()
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        sql = """
            SELECT * FROM content 
            WHERE type = ? AND (LOWER(name) LIKE ? OR code = ?)
            ORDER BY id DESC
        """
        like_q = f"%{query_clean}%"
        try:
            code_q = int(query_clean)
        except:
            code_q = -1
        async with db.execute(sql, (ctype, like_q, code_q)) as cursor:
            return await cursor.fetchall()

async def update_content_field(content_id: int, field: str, value):
    valid_fields = ['name', 'year', 'quality', 'genre', 'code']
    if field not in valid_fields:
        raise ValueError("Invalid field")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE content SET {field} = ? WHERE id = ?", (value, content_id))
        await db.commit()

async def clear_content_files(content_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM content_files WHERE content_id = ?", (content_id,))
        await db.commit()

async def delete_content_completely(content_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM content_files WHERE content_id = ?", (content_id,))
        await db.execute("DELETE FROM keywords WHERE content_id = ?", (content_id,))
        await db.execute("DELETE FROM content WHERE id = ?", (content_id,))
        await db.commit()

