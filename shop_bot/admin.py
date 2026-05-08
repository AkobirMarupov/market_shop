from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, OrderChat, Message



class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at', 'preview_content')
    fields = ('sender_type', 'text', 'preview_content', 'latitude', 'longitude')
    can_delete = False

    # Inline ichida preview ko'rsatish funksiyasi
    def preview_content(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" style="border-radius:5px;"/>', obj.image.url)
        if obj.video:
            return "🎥 Video"
        if obj.file:
            return "📄 Fayl/PDF"
        return "Matn"
    preview_content.short_description = "Media"

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'full_name', 'username', 'phone_number', 'created_at')
    search_fields = ('full_name', 'username', 'chat_id', 'phone_number')
    list_filter = ('created_at',)


@admin.register(OrderChat)
class OrderChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__full_name', 'customer__chat_id', 'product__name')
    inlines = [MessageInline]
    list_editable = ('status',)
    raw_id_fields = ('customer', 'product') # Katta bazada qidirishni osonlashtiradi


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_chat', 'sender_type', 'short_text', 'has_media', 'created_at')
    readonly_fields = ('created_at', 'display_media')

    def short_text(self, obj):
        return (obj.text[:50] + '...') if obj.text and len(obj.text) > 50 else obj.text

    def has_media(self, obj):
        icons = ""
        if obj.image: icons += "🖼 "
        if obj.video: icons += "🎥 "
        if obj.file: icons += "📄 "
        return icons or "➖"
    has_media.short_description = "Media"

    def display_media(self, obj):
        html = ""
        if obj.image:
            html += format_html('<img src="{}" width="200" style="margin-bottom:10px; display:block; border-radius:5px;"/>', obj.image.url)
        if obj.video:
            html += format_html('<video src="{}" width="300" controls style="display:block; margin-bottom:10px;"></video>', obj.video.url)
        if obj.file:
            html += format_html('<a href="{}" target="_blank">📄 Faylni yuklab olish</a>', obj.file.url)
        return format_html(html) if html else "Media yo'q"

    