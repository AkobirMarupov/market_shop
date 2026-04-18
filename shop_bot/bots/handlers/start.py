from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile  # Faylni yuborish uchun kerak

from shop_bot.bots.states import ChatStates
from shop_bot.bots.utils import get_product

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message, command: CommandObject, state: FSMContext):
    args = command.args 

    if not args:
        await message.answer("Assalomu alaykum! Iltimos, kanal tugmasidan foydalaning.")
        return

    product = await get_product(int(args))
    if not product:
        await message.answer("Mahsulot topilmadi.")
        return

    await state.update_data(product_id=product.id)
    await state.set_state(ChatStates.waiting_for_question)

    # product.name va product.price sizning modelingizda borligiga ishonch hosil qiling
    caption = (
        f"📦 <b>{product.name}</b>\n"
        f"💰 Narxi: {product.price} so'm\n\n"
        "Mahsulot bo'yicha savolingizni yozishingiz mumkin."
    )
    
    # AGAR RASM BO'LSA:
    if product.image:
        try:
            # product.image.path — faylning kompyuteringizdagi to'liq manzili
            image_file = FSInputFile(product.image.path)
            await message.answer_photo(
                photo=image_file, 
                caption=caption,
                parse_mode="HTML"
            )
        except Exception as e:
            # Agar rasm fayli topilmasa yoki xato bersa, faqat tekstni yuboramiz
            await message.answer(caption, parse_mode="HTML")
    else:
        # Rasm bo'lmasa faqat tekst
        await message.answer(caption, parse_mode="HTML")