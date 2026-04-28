import asyncio
import logging
from django.core.management.base import BaseCommand
from shop_bot.bots.loader import bot, dp

class Command(BaseCommand):
    help = 'Telegram botni Django bilan birga ishga tushirish'

    def handle(self, *args, **options):
        # Logger sozlamalari
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

        async def main():
            # Circular Import oldini olish uchun importlar funksiya ichida
            from shop_bot.bots.handlers import start, chat
            
            # Routerlarni ulash
            dp.include_routers(
                start.router,
                chat.router
            )
            
            self.stdout.write(self.style.SUCCESS("🚀 Bot ishga tushdi..."))
            
            # Eski xabarlarni tozalash va pollingni boshlash
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write(self.style.WARNING("\n🛑 Bot to'xtatildi!"))