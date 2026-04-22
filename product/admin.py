from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'slug', 'is_subcategory')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)
    search_fields = ('name', 'slug')

    def is_subcategory(self, obj):
        if obj.parent:
            return format_html('<span style="color: green;">{}</span>', "? Subkategoriya")
        return format_html('<b style="color: blue;">{}</b>', "Asosiy")
    
    is_subcategory.short_description = "Turi"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    list_display = ('display_image', 'name', 'brand', 'price', 'currency', 'size', 'color', 'category')
    list_filter = ('category', 'brand', 'color')
    search_fields = ('name', 'brand', 'size')
    fields = (
        'owner', 'name', 'category', 'brand', 
        ('price', 'currency'), 
        ('size', 'color', 'material'), 
        'description', 'image', 'telegram_message_id'
    )

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover;" />',
                obj.image.url
            )
        return "Rasm yo'q"
    
    display_image.short_description = 'Rasm'