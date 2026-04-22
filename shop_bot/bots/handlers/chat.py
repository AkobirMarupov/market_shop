import logging
from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile

# Modellarni import qilamiz
from shop_bot.models import BotUser, Message, Product
from shop_bot.bots.states import ChatStates 


router = Router()
logger = logging.getLogger(__name__)

@sync_to_async
def save_customer_message(user_data, product_id, text, file_info, lat, lon):
    try:
        user = BotUser.objects.filter(user_id=str(user_data['chat_id'])).first()
        if not user:
            # Agar tasodifan user topilmasa, yaratamiz
            user = BotUser.objects.create(
                user_id=str(user_data['chat_id']),
                name=user_data['full_name'],
                username=user_data['username']
            )

        product = Product.objects.filter(id=product_id).first()

        new_msg = Message(
            user=user,
            post=product,
            message=text,
            latitude=lat,
            longitude=lon,
            status="1"
        )

        if file_info:
            new_msg.image.save(
                file_info['name'], 
                ContentFile(file_info['content']), 
                save=False
            )
        
        new_msg.save()
        return True
    except Exception as e:
        logger.error(f"Bazaga saqlashda xato: {e}")
        return False

@router.message(ChatStates.waiting_for_question)
async def handle_customer_message(message: types.Message, state: FSMContext, bot: Bot):
    """
    Foydalanuvchi savol yuborganda ishlovchi handler
    """
    data = await state.get_data()
    product_id = data.get("product_id")

    if not product_id:
        await message.answer("⚠️ Mahsulot aniqlanmadi. Iltimos, kanal orqali qayta kiring.")
        return

    text = message.text or message.caption or ""
    file_info = None
    lat, lon = None, None

    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude

    if message.photo:
        photo = message.photo[-1] # Eng sifatli rasm
        file = await bot.get_file(photo.file_id)
        content = await bot.download_file(file.file_path)
        file_info = {
            'content': content.read(),
            'name': f"msg_{message.from_user.id}.jpg"
        }

    user_data = {
        'chat_id': message.from_user.id,
        'full_name': message.from_user.full_name,
        'username': message.from_user.username
    }

    success = await save_customer_message(
        user_data=user_data,
        product_id=product_id,
        text=text,
        file_info=file_info,
        lat=lat,
        lon=lon
    )

