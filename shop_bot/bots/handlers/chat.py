from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from shop_bot.bots.states import ChatStates
from shop_bot.bots.utils import save_user_message

router = Router()


@router.message(ChatStates.waiting_for_question)
async def handle_question(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")

    if not product_id:
        await message.answer(
            "Savolingizni qabul qilish uchun avval mahsulotni tanlang.\n"
            "Kanal tugmasini qayta bosing."
        )
        await state.clear()
        return

    full_name = message.from_user.full_name or message.from_user.username or "Foydalanuvchi"
    await save_user_message(
        message.chat.id,
        full_name,
        product_id,
        message.text,
        message.message_id,
    )

    await state.set_state(ChatStates.waiting_for_question)
