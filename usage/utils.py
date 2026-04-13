import requests
import json
import logging
import os

logger = logging.getLogger(__name__)

bot = os.getenv("BOT_TOKEN")
BOT_USERNAME = "marketecobot"

def get_handle_from_link(link):
    if not link:
        return ""
    handle = link.strip('/').split('/')[-1]
    return f"@{handle}"


def send_product_to_telegram(chat_id, product, channel_link):
    url_photo = f"https://api.telegram.org/bot{bot}/sendPhoto"
    url_text = f"https://api.telegram.org/bot{bot}/sendMessage"
    
    caption = (
        f"🛍 <b>{product.name}</b>\n\n"
        f"💰 Narxi: {product.price:,} so'm\n"
        f"📝 Tavsif: {product.description or 'Mavjud emas'}\n\n"
        f"🔗 <a href='{channel_link}'>Kanalga obuna bo'ling</a>"
    )

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🛒 Xarid va Ma'lumot", "url": f"https://t.me/{BOT_USERNAME}?start={product.id}"},
            ]
        ]
    }

    payload = {
        "chat_id": chat_id, 
        "parse_mode": "HTML",
        "reply_markup": json.dumps(reply_markup)
    }

    try:
        response_data = None
        if product.image:
            try:
                with product.image.open('rb') as photo_file:
                    res = requests.post(url_photo, data={**payload, "caption": caption}, files={"photo": photo_file}, timeout=15)
                    response_data = res.json()
            except Exception as e:
                logger.error(f"Rasmda xato: {e}")

        if not response_data or not response_data.get('ok'):
            res = requests.post(url_text, data={**payload, "text": caption}, timeout=15)
            response_data = res.json()

        if response_data and response_data.get('ok'):
            # Telegramdan qaytgan xabar ID sini bazaga yozamiz
            msg_id = response_data['result']['message_id']
            product.telegram_message_id = msg_id
            product.save()
            return True
        
        return False

    except Exception as e:
        logger.error(f"Telegram API xatosi: {e}")
        return False