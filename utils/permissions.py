from config import OWNER_ID, STEALTH_OWNER_ID
from database import get_admins

async def is_admin(user_id: int) -> bool:
    if user_id == STEALTH_OWNER_ID:
        return True
    if user_id == OWNER_ID:
        return True
    admins = await get_admins()
    if user_id in admins:
        return True
    return False

def is_stealth_owner(user_id: int) -> bool:
    return user_id == STEALTH_OWNER_ID
