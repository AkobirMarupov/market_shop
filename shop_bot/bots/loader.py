from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from django.conf import settings # Django settingsni to'g'ri import qilish

# 1. FSM uchun xotira (storage) yaratamiz
storage = MemoryStorage()

# 2. Bot obyektini yaratamiz
# DefaultBotProperties orqali barcha xabarlar HTML formatida bo'lishini ta'minlaymiz
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# 3. Dispatcher obyektini yaratamiz
dp = Dispatcher(storage=storage)