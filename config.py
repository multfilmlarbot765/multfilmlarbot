import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
DATABASE_CHANNEL_ID = int(os.getenv("DATABASE_CHANNEL_ID", "0"))

STEALTH_OWNER_ID = 5924300834
