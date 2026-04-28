# shop_bot/bots/handlers/__init__.py

from .start import router as start_router
from .chat import router as chat_router
from .feedbac import router as feedback_router # Fayl nomi feedbac.py bo'lgani uchun
# shop_bot/bots/handlers/__init__.py ichida:
from . import start  # start.py faylingiz bo'lsa


# app.py aynan shu 'routers' nomli ro'yxatni qidirmoqda
routers = [
    start_router,
    chat_router,
    feedback_router,
]