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
    list_display = ('name', 'price', 'category', 'display_image')
    list_filter = ('category',)
    search_fields = ('name', 'description')

    def display_image(self, obj):
        if obj.image:
            img_url = obj.image.url
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="width: 50px; height: 50px; border-radius: 5px; object-fit: cover;" />'
                '</a>',
                img_url
            )
        return "Rasm yo'q"
    display_image.short_description = 'Image'

