import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async

from shop_bot.models import BotUser
from shop_bot.bots.states import ChatStates
from product.models import Product

router = Router()
logger = logging.getLogger(__name__)

@sync_to_async
def get_or_create_bot_user(user_id, full_name, username):
    user, created = BotUser.objects.update_or_create(
        user_id=str(user_id),
        defaults={
            'name': full_name,
            'username': username
        }
    )
    return user

@sync_to_async
def get_post_by_id(post_id):
    return Product.objects.filter(id=post_id).first()

@router.message(CommandStart())
async def start_command(message: types.Message, command: CommandObject, state: FSMContext):
    args = command.args

    await get_or_create_bot_user(
        message.from_user.id, 
        message.from_user.full_name, 
        message.from_user.username
    )

    if not args:
        await message.answer(
            "👋 Xush kelibsiz!\n\nMahsulotlar haqida ma'lumot olish uchun kanalimizdagi "
            "maxsus havolalar orqali kiring."
        )
        return

    product = await get_post_by_id(args)

    if not product:
        await message.answer("⚠️ Kechirasiz, ushbu mahsulot topilmadi yoki o'chirilgan.")
        return

    await state.update_data(product_id=product.id)
    await state.set_state(ChatStates.waiting_for_question)

    
    currency_label = product.get_currency_display()
    
    caption = (
        f"📦 <b>{product.name}</b>\n\n"
        f"📝 Ma'lumot: {product.description or 'Mavjud emas'}\n"
        f"🎨 Rangi: {product.color or 'Korsatilmagan'}\n"
        f"📏 O'lchami: {product.size or 'Korsatilmagan'}\n"
        f"💰 Narxi: <b>{product.price:,.0f} {currency_label}</b>\n\n"
        "💬 Ushbu mahsulot bo'yicha savolingiz bormi? \n"
        "Pastdan yozib qoldiring, adminlarimiz javob berishadi."
    )

    if product.image:
        try:
            photo = FSInputFile(product.image.path)
            await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Rasm yuborishda xato: {e}")
            await message.answer(caption, parse_mode="HTML")
    else:
        await message.answer(caption, parse_mode="HTML")