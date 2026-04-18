from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

# O'zingizning app va model nomingizni to'g'ri kiriting
from shop_bot.models import TelegramNotification 
from shop_bot.bots.states import ChatStates

router = Router()

@sync_to_async
def create_notification(product_id, full_name, username, chat_id, message_text):
    # Siz ko'rsatgan modelga ma'lumotni yozamiz
    return TelegramNotification.objects.create(
        product_id=product_id,
        full_name=full_name,
        username=username,
        chat_id=chat_id,
        message=message_text,
        status='yangi'
    )

@router.message(ChatStates.waiting_for_question)
async def handle_customer_message(message: types.Message, state: FSMContext):
    # State'dan mahsulot ID'sini olamiz
    data = await state.get_data()
    product_id = data.get("product_id")

    if not message.text:
        await message.answer("Iltimos, savolingizni matn ko'rinishida yozing.")
        return

    # 1. Bazaga saqlash (Django modeli orqali)
    await create_notification(
        product_id=product_id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        chat_id=message.from_user.id,
        message_text=message.text
    )

    
    # 3. Holatni tozalaymiz (State'ni yopamiz)
    await state.clear()