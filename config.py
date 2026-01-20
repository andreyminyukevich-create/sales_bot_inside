import os

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Admin & Owner
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0"))

# OpenAI (для ИИ-слоя, потом)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Studio Info
STUDIO_ADDRESS = "Инсайд Детейлинг\nТамбов, д. Красненькое. Северная 16в"
STUDIO_MAP_URL = "https://yandex.ru/maps/-/CLhLBV0T"

# Working Hours
WEEKDAY_HOURS = "10:00–19:00"
SATURDAY_HOURS = "11:00–18:00"
SUNDAY_HOURS = "выходной (но принять авто можно, админ подтвердит)"

# Mode
MODE = os.getenv("MODE", "production")
