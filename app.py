import os
import django
import asyncio
import logging

# 1-QADAM: Sozlamalarni ko'rsatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 

# 2-QADAM: Djangoni ishga tushirish (BU HAMMASIDAN OLDIN BO'LISHI SHART)
django.setup()

# 3-QADAM: Faqat setup'dan keyin bot va handlerlarni import qilish
from shop_bot.bots import handlers 
from shop_bot.bots.loader import bot, dp

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Routerlarni ulash
    for router in handlers.routers:
        dp.include_router(router)
    
    print("Bot ishga tushdi...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi!")