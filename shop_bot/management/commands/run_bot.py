import asyncio
import logging
from django.core.management.base import BaseCommand
from shop_bot.bots.loader import bot, dp

class Command(BaseCommand):
    help = 'Telegram botni Django bilan birga ishga tushirish'

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

        async def main():
            from shop_bot.bots.handlers import start, chat
            
            dp.include_routers(
                start.router,
                chat.router
            )
            
            self.stdout.write(self.style.SUCCESS("🚀 Bot ishga tushdi..."))
            
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write(self.style.WARNING("\n🛑 Bot to'xtatildi!"))