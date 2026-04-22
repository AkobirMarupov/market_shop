import os
import sys
import django
import asyncio
import logging

# 1. Loyiha yo'lini sozlash
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. Django muhitini yuklash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
django.setup()

# 3. Importlarni django.setup() dan keyin qilamiz
from shop_bot.bots.loader import bot, dp
from shop_bot.bots.handlers import start, chat # Alohida routerlarni import qilish

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Routerlarni tartib bilan ulash
    # include_router bir nechta routerni ham qabul qiladi
    dp.include_routers(
        start.router,
        chat.router
    )
    
    print("🚀 Bot ishga tushdi...")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Bot to'xtatildi!")