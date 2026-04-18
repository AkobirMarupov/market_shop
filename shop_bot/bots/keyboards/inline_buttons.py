from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_product_buttons(product_id: int, bot_username: str):
    url = f"https://t.me/{bot_username}?start={product_id}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛒 Xarid va Ma'lumot", url=url)
        ]
    ])
    return keyboard