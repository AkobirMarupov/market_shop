import requests
from io import BytesIO
from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from shop_bot.bots.states import ChatStates
from shop_bot.bots.utils import get_product

router = Router()
# API manzilingizni tekshiring (oxirida /bot/feedback/ bo'lishi kerak)
API_URL = "http://127.0.0.1:8000/api/bot/feedback/" 

@router.message(Command(commands=["feedback"]))
async def start_feedback(message: Message, state: FSMContext):
    text = message.text.split()
    if len(text) < 2 or not text.isdigit():
        await message.answer("❌ Feedback uchun mahsulot ID sini yozing.\nMasalan: /feedback 1")
        return

    product_id = int(text)
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
    
    # 1. Asosiy ma'lumotlar
    feedback_data = {
        "user_id": message.from_user.id,
        "body": message.caption or message.text or "",
        "post": post_id
    }
    files = {}

    # 2. Location (Kenglik va Uzunlik)
    if message.location:
        feedback_data["latitude"] = message.location.latitude
        feedback_data["longitude"] = message.location.longitude

    # 3. Media fayllarni yuklab olish funksiyasi
    async def download_tg_file(file_id):
        file = await message.bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
        resp = requests.get(file_url, timeout=20)
        if resp.status_code == 200:
            return BytesIO(resp.content)
        return None

    # 4. Fayl turini aniqlash va yuklash
    if message.photo:
        file_io = await download_tg_file(message.photo[-1].file_id)
        if file_io: files["file"] = ("image.jpg", file_io, "image/jpeg")

    elif message.video:
        file_io = await download_tg_file(message.video.file_id)
        if file_io: files["file"] = ("video.mp4", file_io, "video/mp4")

    elif message.document:
        file_io = await download_tg_file(message.document.file_id)
        if file_io: files["file"] = (message.document.file_name, file_io, message.document.mime_type)

    elif message.animation: # GIF uchun
        file_io = await download_tg_file(message.animation.file_id)
        if file_io: files["file"] = ("animation.gif", file_io, "image/gif")

    # API ga yuborish
    try:
        response = requests.post(API_URL, data=feedback_data, files=files, timeout=30)
        if response.status_code == 201:
            await message.reply("✅ Fikringiz qabul qilindi. Rahmat!")
            await state.clear()
        else:
            await message.reply(f"❌ Xatolik yuz berdi: {response.status_code}")
    except Exception as e:
        print(f"DEBUG API ERROR: {e}")
        await message.reply("❌ Server bilan bog'lanishda xato.")