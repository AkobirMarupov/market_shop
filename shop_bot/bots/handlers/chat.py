import logging
from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile

from shop_bot.models import OrderChat, Message as DB_Message
from shop_bot.bots.states import ChatStates

router = Router()
logger = logging.getLogger(__name__)


@sync_to_async
def save_customer_message(order_chat_id, text, file_info, lat, lon):
    try:
        chat = OrderChat.objects.get(id=order_chat_id)
        
        new_msg = DB_Message(
            order_chat=chat,
            owner=chat.owner,
            sender_type=1,    
            text=text,
            latitude=lat or 0,
            longitude=lon or 0
        )

        if file_info:
            content = ContentFile(file_info['content'], name=file_info['name'])
            
            if file_info['type'] == 'image':
                new_msg.image.save(file_info['name'], content, save=False)
            elif file_info['type'] == 'video':
                new_msg.video.save(file_info['name'], content, save=False)
            else:
                new_msg.file.save(file_info['name'], content, save=False)
        
        new_msg.save()
        
        if chat.status == 'new':
            chat.status = 'active'
            chat.save()
            
        return True
    except Exception as e:
        logger.error(f"Bazaga saqlashda xato: {e}")
        return False
    

@router.message(ChatStates.waiting_for_question)
async def handle_customer_message(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_chat_id = data.get("order_chat_id") 

    if not order_chat_id:
        return

    text = message.text or message.caption or ""
    file_info = None
    lat, lon = (message.location.latitude, message.location.longitude) if message.location else (None, None)

    try:
        media = None
        m_type = None
        f_name = ""

        if message.photo:
            media = message.photo[-1] 
            m_type = 'image'
            f_name = f"img_{message.message_id}.jpg"
        elif message.video:
            media = message.video
            m_type = 'video'
            f_name = getattr(media, 'file_name', None) or f"vid_{message.message_id}.mp4"
            
            file = await bot.get_file(media.file_id)
            if file.file_path:
                content = await bot.download_file(file.file_path)
                file_bytes = content.getvalue()
                
                file_info = {
                    'content': file_bytes,
                    'name': f_name,
                    'type': m_type
                }
                await save_customer_message(order_chat_id, text, file_info, lat, lon)
        elif message.document:
            media = message.document
            m_type = 'pdf' if message.document.mime_type == 'application/pdf' else 'file'
            f_name = getattr(media, 'file_name', f"doc_{message.message_id}")

        if media:
            file = await bot.get_file(media.file_id)
            content = await bot.download_file(file.file_path)
            file_bytes = content.getvalue() 
            
            file_info = {
                'content': file_bytes, 
                'name': f_name, 
                'type': m_type
            }
            await save_customer_message(order_chat_id, text, file_info, lat, lon)
        else:
            await save_customer_message(order_chat_id, text, None, lat, lon)

    except Exception as e:
        logger.error(f"Handlerda xatolik: {e}")