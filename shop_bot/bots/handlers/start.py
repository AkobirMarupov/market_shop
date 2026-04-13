from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext

from shop_bot.bots.states import ChatStates
from shop_bot.bots.utils import get_product

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    text = message.text or ""
    args = ""
    if " " in text:
        args = text.split(" ", 1)[1].strip()

    if not args:
        await message.answer(
            "Assalomu alaykum! Iltimos, kanal tugmasidagi 'Xarid va Ma'lumot' tugmasini bosib mahsulotni tanlang."
        )
        return

    if not args.isdigit():
        await message.answer("Mahsulot identifikatori noto‘g‘ri. Iltimos, kanal tugmasini qayta bosing.")
        return

    product = await get_product(int(args))
    if not product:
        await message.answer("Bunday mahsulot topilmadi.")
        return

    await state.update_data(product_id=product.id)
    await state.set_state(ChatStates.waiting_for_question)

    await message.answer(
        f"📦 <b>{product.name}</b>\n"
        f"💰 Narxi: {product.price} so'm\n\n"
        "Mahsulot bo'yicha savolingizni yozishingiz mumkin.\n"
        "Xaridingizni boshlashingiz mumkin."
        , parse_mode="HTML"
    )
