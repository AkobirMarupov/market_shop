import requests
from django.conf import settings
# Muhim: Modelni import qilishda loyiha nomidan foydalaning
from shop_bot.models import Product 
from asgiref.sync import sync_to_async

@sync_to_async
def get_product(product_id):
    """
    ID bo'yicha mahsulotni bazadan qidirish (Asinxron wrapper bilan)
    """
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None

def send_telegram_message(chat_id, text):
    """
    Django signallari yoki boshqa joydan xabar yuborish uchun (Sinxron)
    """
    token = settings.BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Telegram yuborishda xato: {e}")
        return None