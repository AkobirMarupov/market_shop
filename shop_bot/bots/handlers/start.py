import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from shop_bot.models import TelegramUser, OrderChat, UsageLink
from product.models import Product
from shop_bot.bots.states import ChatStates

User = get_user_model()
router = Router()
logger = logging.getLogger(__name__)

@sync_to_async
def get_or_create_session(user_id, full_name, username, link_id, product_id):
    try:
        # 1. Mijozni yaratish yoki yangilash
        tg_user, _ = TelegramUser.objects.update_or_create(
            chat_id=user_id,
            defaults={'full_name': full_name or "", 'username': username or ""}
        )
        
        product = Product.objects.filter(id=int(product_id)).first()
        if not product: 
            return None, None, None

        usage_link = None
        sotuvchi = product.owner  # Default: mahsulot egasi

        if link_id and str(link_id).isdigit():
            usage_link = UsageLink.objects.filter(id=int(link_id)).select_related('usage__user').first()
            if usage_link and usage_link.usage.user:
                sotuvchi = usage_link.usage.user

        if not sotuvchi:
            sotuvchi = User.objects.filter(is_superuser=True).first()

        chat_session = OrderChat.objects.create(
            customer=tg_user,
            product=product,
            owner=sotuvchi,
            usage_link=usage_link,
            status='new'
        )
        
        return tg_user, chat_session, product
    except Exception as e:
        logger.error(f"Sessiya yaratishda xato: {e}")
        return None, None, None

@router.message(CommandStart())
async def start_command(message: types.Message, command: CommandObject, state: FSMContext):
    args = command.args
    
    if not args:
        await message.answer("👋 Xush kelibsiz! Mahsulot sotib olish uchun kanaldagi havolalardan foydalaning.")
        return

    try:
        link_id = None
        product_id = None

        if "_" in args:
            parts = args.split("_")
            link_id = parts
            product_id = parts
        else:
            product_id = args

        tg_user, chat_session, product = await get_or_create_session(
            message.from_user.id, 
            message.from_user.full_name, 
            message.from_user.username,
            link_id,
            product_id
        )

        if not chat_session:
            await message.answer("⚠️ Kechirasiz, mahsulot topilmadi.")
            return

        await state.set_state(ChatStates.waiting_for_question)
        await state.update_data(order_chat_id=chat_session.id)

        price = "{:,}".format(product.price).replace(",", " ")
        caption = (
            f"🛍 <b>{product.name}</b>\n\n"
            f"📝 <b>Ma'lumot:</b> {product.description or 'Mavjud emas'}\n"
            f"💰 <b>Narxi:</b> {price} so'm\n\n"
            f"💬 Savolingiz bo'lsa yozing, adminlarimiz javob berishadi."
        )

        if product.image:
            photo = FSInputFile(product.image.path)
            await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
        else:
            await message.answer(caption, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Startda xato: {e}")