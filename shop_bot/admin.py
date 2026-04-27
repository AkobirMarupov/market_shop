from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, OrderChat, Message



class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at', 'preview_content')
    fields = ('sender_type', 'text', 'preview_content', 'latitude', 'longitude')
    can_delete = False
    
    def preview_content(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 80px; height:auto; border-radius:5px;">', obj.image.url)
        if obj.video:
            return format_html('<span style="color: blue;">🎥 Video mavjud</span>')
        if obj.file:
            return format_html('<a href="{}" target="_blank">📄 Faylni ochish</a>', obj.file.url)
        if obj.latitude and obj.longitude:
            return format_html('<span style="color: green;">📍 Lokatsiya</span>')
        return "Fayl yo'q"
    
    preview_content.short_description = "Media/Fayl"


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
    list_filter = ('sender_type', 'is_image', 'is_video', 'is_pdf', 'created_at')
    readonly_fields = ('created_at', 'display_media')
    search_fields = ('text', 'order_chat__customer__full_name')

    def short_text(self, obj):
        if obj.text:
            return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
        return "Matn yo'q"
    short_text.short_description = "Xabar matni"

    def has_media(self, obj):
        return obj.is_image or obj.is_video or obj.is_pdf
    has_media.boolean = True
    has_media.short_description = "Media bormi?"

    def display_media(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px; height:auto;">', obj.image.url)
        if obj.video:
            return format_html('<video width="320" height="240" controls><source src="{}" type="video/mp4"></video>', obj.video.url)
        if obj.file:
            return format_html('<a href="{}" target="_blank">Faylni yuklab olish (PDF/Doc)</a>', obj.file.url)
        return "Media yo'q"
    display_media.short_description = "Media ko'rinishi"