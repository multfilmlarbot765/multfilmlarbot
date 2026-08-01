import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = os.getenv('MONGODB_URI')

client = None
db = None

async def init_db():
    global client, db
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not set in environment variables.")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.get_database() # Uses default db from URI
    
    # Create indexes for fast lookup and uniqueness
    await db.users.create_index("id", unique=True)
    await db.admins.create_index("id", unique=True)
    await db.content.create_index("id", unique=True)
    await db.content.create_index("code", unique=True)
    await db.settings.create_index("key", unique=True)
    await db.feedback.create_index("id", unique=True)
    await db.activity_logs.create_index("user_id")
    await db.activity_logs.create_index("timestamp")

    # Default settings
    default_settings = [
        ('stealth_media_log_enabled', 'True'),
        ('custom_footer', ''),
        ('force_sub_channel', ''),
        ('movies_channel_link', ''),
        ('main_channel_url', 'https://t.me/multifilmlarobot')
    ]
    for key, val in default_settings:
        await db.settings.update_one({'key': key}, {'$setOnInsert': {'value': val}}, upsert=True)

async def ping_db():
    if client:
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

async def close_db():
    if client:
        client.close()
        print("MongoDB connection closed.")

async def get_next_sequence(name: str) -> int:
    ret = await db.counters.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=True
    )
    return ret['seq']

# --- Users ---
async def get_or_create_user(user_id: int, username: str, full_name: str, language: str = 'uz'):
    import datetime
    now = datetime.datetime.now()
    user = await db.users.find_one_and_update(
        {"id": user_id},
        {"$set": {
            "username": username,
            "full_name": full_name,
            "language": language,
            "last_active_at": now
        },
        "$setOnInsert": {
            "joined_date": now,
            "is_active": True
        }},
        upsert=True,
        return_document=True
    )
    # If the user was just inserted, 'joined_date' and 'last_active_at' will be very close.
    # We can determine if new by checking if created right now. But let's just return the user.
    return user

async def add_user(user_id: int, name: str, username: str):
    # Legacy wrapper
    import datetime
    now = datetime.datetime.now()
    user = await db.users.find_one_and_update(
        {"id": user_id},
        {"$set": {
            "username": username,
            "full_name": name,
            "last_active_at": now
        },
        "$setOnInsert": {
            "joined_date": now,
            "is_active": True,
            "language": "uz"
        }},
        upsert=True,
        return_document=False # Returns document BEFORE update (None if inserted)
    )
    return user is None

async def update_user_status(user_id: int, is_active: bool):
    await db.users.update_one({"id": user_id}, {"$set": {"is_active": is_active}})

async def get_user(user_id: int):
    return await db.users.find_one({"id": user_id})

# --- Admins ---
async def get_admins():
    cursor = db.admins.find({})
    admins = await cursor.to_list(length=None)
    return [admin['id'] for admin in admins]

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
    await db.admins.update_one({"id": user_id}, {"$setOnInsert": {"added_by": added_by}}, upsert=True)

async def remove_admin(user_id: int):
    await db.admins.delete_one({"id": user_id})

# --- Content ---
async def add_content(ctype: str, name: str, code: int, year: str, quality: str, genre: str, caption: str = ""):
    import datetime
    cid = await get_next_sequence('content_id')
    await db.content.insert_one({
        "id": cid,
        "type": ctype,
        "name": name,
        "code": code,
        "year": year,
        "quality": quality,
        "genre": genre,
        "caption": caption,
        "views_count": 0,
        "download_count": 0,
        "added_at": datetime.datetime.now(),
        "files": [],
        "keywords": []
    })
    return cid

async def add_content_file(content_id: int, file_id: str):
    await db.content.update_one({"id": content_id}, {"$push": {"files": file_id}})

async def add_keyword(content_id: int, keyword: str):
    await db.content.update_one({"id": content_id}, {"$push": {"keywords": keyword.lower().strip()}})

async def get_content_by_code(code: int):
    # Automatically increment views_count whenever fetched by code
    return await db.content.find_one_and_update(
        {"code": code},
        {"$inc": {"views_count": 1}},
        return_document=True
    )

async def get_files_by_content_id(content_id: int):
    content = await db.content.find_one({"id": content_id})
    return content.get("files", []) if content else []

async def increment_download(content_id: int):
    await db.content.update_one({"id": content_id}, {"$inc": {"download_count": 1}})

async def search_content_by_keyword(keyword: str):
    kw = keyword.lower().strip()
    cursor = db.content.find({
        "$or": [
            {"name": {"$regex": kw, "$options": "i"}},
            {"keywords": kw}
        ]
    })
    return await cursor.to_list(length=None)

async def get_top_content(limit: int = 10):
    cursor = db.content.find().sort("download_count", -1).limit(limit)
    return await cursor.to_list(length=None)

async def get_random_content():
    cursor = db.content.aggregate([{"$sample": {"size": 1}}])
    res = await cursor.to_list(length=1)
    return res[0] if res else None

async def get_next_code():
    cursor = db.content.find().sort("code", -1).limit(1)
    res = await cursor.to_list(length=1)
    return (res[0]["code"] if res else 1000) + 1

# --- Statistics ---
async def get_total_users():
    return await db.users.count_documents({})

async def get_today_users():
    import datetime
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return await db.users.count_documents({"joined_date": {"$gte": today}})

async def get_total_movie_downloads():
    pipeline = [{"$match": {"type": "kino"}}, {"$group": {"_id": None, "total": {"$sum": "$download_count"}}}]
    res = await db.content.aggregate(pipeline).to_list(length=1)
    return res[0]["total"] if res else 0

async def get_total_cartoon_downloads():
    pipeline = [{"$match": {"type": "multfilm"}}, {"$group": {"_id": None, "total": {"$sum": "$download_count"}}}]
    res = await db.content.aggregate(pipeline).to_list(length=1)
    return res[0]["total"] if res else 0

# --- Activity Logs ---
async def log_activity(user_id: int, action_type: str, detail: str):
    import datetime
    await db.activity_logs.insert_one({
        "user_id": user_id,
        "action_type": action_type,  # "search" or "download"
        "detail": detail,
        "timestamp": datetime.datetime.now()
    })

# --- Settings ---
async def get_setting(key: str):
    doc = await db.settings.find_one({"key": key})
    return doc["value"] if doc else None

async def set_setting(key: str, value: str):
    await db.settings.update_one({"key": key}, {"$set": {"value": str(value)}}, upsert=True)

# --- Feedback ---
async def add_feedback(user_id: int, f_type: str, message: str):
    fid = await get_next_sequence('feedback_id')
    import datetime
    await db.feedback.insert_one({
        "id": fid,
        "user_id": user_id,
        "type": f_type,
        "message": message,
        "status": "pending",
        "created_at": datetime.datetime.now()
    })
    return fid

async def get_pending_feedback(f_type: str):
    cursor = db.feedback.find({"type": f_type, "status": "pending"}).sort("id", 1)
    return await cursor.to_list(length=None)

async def mark_feedback_replied(feedback_id: int):
    await db.feedback.update_one({"id": feedback_id}, {"$set": {"status": "replied"}})

async def delete_feedback(feedback_id: int):
    await db.feedback.delete_one({"id": feedback_id})

# --- Media Editing & Pagination ---
async def get_content_count(ctype: str):
    return await db.content.count_documents({"type": ctype})

async def get_content_paginated(ctype: str, limit: int, offset: int):
    cursor = db.content.find({"type": ctype}).sort("id", -1).skip(offset).limit(limit)
    return await cursor.to_list(length=None)

async def search_content_wildcard(query: str, ctype: str):
    query_clean = query.lower().strip()
    try:
        code_q = int(query_clean)
    except ValueError:
        code_q = -1
        
    filter_doc = {
        "type": ctype,
        "$or": [
            {"name": {"$regex": query_clean, "$options": "i"}},
            {"code": code_q}
        ]
    }
    cursor = db.content.find(filter_doc)
    return await cursor.to_list(length=None)

async def update_content_field(content_id: int, field: str, value):
    valid_fields = ['name', 'year', 'quality', 'genre', 'code']
    if field not in valid_fields:
        raise ValueError("Invalid field")
    await db.content.update_one({"id": content_id}, {"$set": {field: value}})

async def clear_content_files(content_id: int):
    await db.content.update_one({"id": content_id}, {"$set": {"files": []}})

async def delete_content_completely(content_id: int):
    await db.content.delete_one({"id": content_id})
