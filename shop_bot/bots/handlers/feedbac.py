import requests
import logging
from io import BytesIO
from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from shop_bot.bots.states import ChatStates
from shop_bot.bots.utils import get_product

router = Router()
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8000/api/bot/feedback/" 

@router.message(Command(commands=["feedback"]))
async def start_feedback(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("❌ Feedback uchun mahsulot ID sini yozing.\nMasalan: /feedback 1")
        return

    product_id = int(args[1])
    product = await get_product(product_id)
    if not product:
        await message.answer("❌ Mahsulot topilmadi.")
        return

    await state.update_data(post_id=product_id)
    await state.set_state(ChatStates.waiting_for_comment)
    
    await message.answer(
        f"📩 <b>{product.name}</b> uchun fikringizni yuboring.\n"
        "Matn, rasm, video, fayl yoki lokatsiya yuborishingiz mumkin."
    )

@router.message(ChatStates.waiting_for_comment)
async def handle_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("post_id")
    
    feedback_data = {
        "user_id": message.from_user.id,
        "message": message.caption or message.text or "", 
        "post": post_id,
        "status": "1" 
    }
    files = {}

    if message.location:
        feedback_data["latitude"] = message.location.latitude
        feedback_data["longitude"] = message.location.longitude

    async def download_tg_file(file_id):
        try:
            file = await message.bot.get_file(file_id)
            file_io = BytesIO()
            await message.bot.download_file(file.file_path, file_io)
            file_io.seek(0) 
            return file_io
        except Exception as e:
            logger.error(f"Fayl yuklashda xato: {e}")
            return None

    if message.photo:
        file_io = await download_tg_file(message.photo[-1].file_id)
        if file_io: 
            files["image"] = ("image.webp", file_io, "image/webp") 

    elif message.video or message.document or message.animation:
        f_id = (message.video or message.document or message.animation).file_id
        f_name = getattr(message.document, 'file_name', 'file.mp4')
        file_io = await download_tg_file(f_id)
        if file_io: 
            files["file"] = (f_name, file_io, "application/octet-stream")

    try:
        response = requests.post(API_URL, data=feedback_data, files=files, timeout=30)
        
        if response.status_code in [200, 201]:
            await message.reply("✅ Fikringiz qabul qilindi. Rahmat!")
            await state.clear()
        else:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            await message.reply(f"❌ Xatolik yuz berdi (Server javobi: {response.status_code})")
            
    except Exception as e:
        logger.error(f"DEBUG API CONNECTION ERROR: {e}")
        await message.reply("❌ Server bilan bog'lanishda xato. Keyinroq urinib ko'ring.")