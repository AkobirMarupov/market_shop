from asgiref.sync import sync_to_async
from product.models import Product
from shop_bot.models import ChatSession, ChatMessage, ProductComment

@sync_to_async
def save_user_message(chat_id, full_name, product_id, text, message_id=None):
    product = Product.objects.get(id=product_id)
    session, _ = ChatSession.objects.get_or_create(
        chat_id=chat_id,
        product=product,
        defaults={'full_name': full_name}
    )
    message = ChatMessage.objects.create(session=session, text=text, is_from_admin=False)
    ProductComment.objects.create(
        product=product,
        user_chat_id=chat_id,
        full_name=full_name,
        text=text,
        telegram_message_id=message_id or 0
    )
    return message

@sync_to_async
def get_product(product_id):
    return Product.objects.filter(id=product_id).first()