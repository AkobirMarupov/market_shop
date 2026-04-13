from django.contrib import admin, messages
from django.conf import settings
from django.utils.html import format_html
import requests

from shop_bot.models import ChatSession, ChatMessage, ProductComment

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('is_from_admin', 'text', 'display_media', 'display_location', 'created_at')
    fields = ('is_from_admin', 'text', 'display_media', 'display_location', 'created_at')
    can_delete = False

    def display_media(self, obj):
        if obj.media_file:
            if obj.file_type == 'photo':
                return format_html('<img src="{}" style="max-width: 200px; border-radius: 5px;" />', obj.media_file.url)
            return format_html('<a href="{}" target="_blank">? Faylni yuklab olish ({})</a>', obj.media_file.url, obj.file_type)
        return "Matnli xabar"
    display_media.short_description = "Media"

    def display_location(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://www.google.com/maps?q={},{}" target="_blank">? Xaritada ko\'rish</a>',
                obj.latitude, obj.longitude
            )
        return "-"
    display_location.short_description = "Lokatsiya"

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'product', 'chat_id', 'is_active', 'created_at')
    list_filter = ('is_active', 'product')
    search_fields = ('full_name', 'chat_id', 'product__name')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    # 3-O'ZGARISH: Ro'yxatda media borligini bildirish
    list_display = ('session', 'is_from_admin', 'short_text', 'file_type', 'created_at')
    list_filter = ('is_from_admin', 'file_type')
    search_fields = ('text', 'session__full_name')

    def short_text(self, obj):
        # Agar matn bo'lsa, uni qisqartirib qaytaramiz
        if obj.text:
            return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text
        
        # Agar matn bo'lmasa va file_type mavjud bo'lsa
        if obj.file_type:
            return f"[{obj.file_type.capitalize()} xabari]"
        
        # Agar na matn va na file_type bo'lsa (masalan, eski xabarlar)
        return "[Noma'lum xabar]"
    
    short_text.short_description = 'Xabar mazmuni'

@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'product', 'is_replied', 'created_at')
    readonly_fields = ('product', 'full_name', 'user_chat_id', 'text')
    fields = ('product', 'full_name', 'user_chat_id', 'text', 'reply_text', 'is_replied')

    def save_model(self, request, obj, form, change):
        if obj.reply_text and not obj.is_replied:
            # Bot token settingsdan olinishi aniqlandi
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": obj.user_chat_id,
                "text": (
                    f"<b>Savolingizga javob berildi!</b>\n\n"
                    f"? Sizning so'rovingiz: <i>{obj.text}</i>\n\n"
                    f"? <b>Admin javobi:</b> {obj.reply_text}\n\n"
                    f"? Mahsulot: {obj.product.name}"
                ),
                "parse_mode": "HTML"
            }
            try:
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    obj.is_replied = True
                    messages.success(request, f"{obj.full_name} foydalanuvchisiga javob yuborildi.")
                else:
                    messages.error(request, f"Telegram API xatosi: {res.status_code}")
            except Exception as e:
                messages.error(request, f"Xatolik: {str(e)}")
        super().save_model(request, obj, form, change)