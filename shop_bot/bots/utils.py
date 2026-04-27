import httpx
import asyncio
from django.conf import settings
from shop_bot.models import Product 
from asgiref.sync import sync_to_async

@sync_to_async
def get_product(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None

async def send_telegram_message(chat_id, text=None, file=None, is_image=False, is_video=False, is_pdf=False, lat=None, lon=None):

    token = settings.BOT_TOKEN
    base_url = f"https://api.telegram.org/bot{token}/"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        if lat is not None and lon is not None and float(lat) != 0:
            url = base_url + "sendLocation"
            data = {"chat_id": chat_id, "latitude": lat, "longitude": lon}
            response = await client.post(url, json=data)

        elif is_image and file:
            url = base_url + "sendPhoto"
            # caption bo'sh bo'lsa xato bermasligi uchun default "" beramiz
            data = {"chat_id": chat_id, "caption": text if text else "", "parse_mode": "HTML"}
            files = {"photo": file}
            response = await client.post(url, data=data, files=files)

        elif is_video and file:
            url = base_url + "sendVideo"
            data = {"chat_id": chat_id, "caption": text if text else "", "parse_mode": "HTML"}
            files = {"video": file}
            response = await client.post(url, data=data, files=files)

        elif is_pdf and file:
            url = base_url + "sendDocument"
            data = {"chat_id": chat_id, "caption": text if text else "", "parse_mode": "HTML"}
            files = {"document": file}
            response = await client.post(url, data=data, files=files)

        elif text:
            url = base_url + "sendMessage"
            data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            response = await client.post(url, json=data)
        
        else:
            return None

        return response.json()