from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Usage, UsageLink, LinkConnect

class BaseOwnerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        if hasattr(self.model, 'user'):
            return qs.filter(user=request.user)
        if hasattr(self.model, 'owner'):
            return qs.filter(owner=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change: 
            if hasattr(obj, 'user'):
                obj.user = request.user
            if hasattr(obj, 'owner'):
                obj.owner = request.user
        super().save_model(request, obj, form, change)

@admin.register(Usage)
class UsageAdmin(BaseOwnerAdmin):
    list_display = ('id', 'title', 'user', 'created_at')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'user__phone_number')
    list_filter = ('created_at',)

@admin.register(UsageLink)
class UsageLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'link', 'usage', 'is_paid', 'is_active')
    list_editable = ('is_paid', 'is_active')
    list_filter = ('is_paid', 'is_active', 'usage__user')
    search_fields = ('link', 'usage__title')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usage__user=request.user)

    def render_change_form(self, request, context, *args, **kwargs):
        """Faqat o'ziga tegishli 'Usage' guruhlarini tanlash imkonini beradi"""
        if not request.user.is_superuser:
            context['adminform'].form.fields['usage'].queryset = Usage.objects.filter(user=request.user)
        return super().render_change_form(request, context, *args, **kwargs)

@admin.register(LinkConnect)
class LinkConnectAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'usage')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(category__owner=request.user)

    def render_change_form(self, request, context, *args, **kwargs):
        if not request.user.is_superuser:
            from product.models import Category
            context['adminform'].form.fields['category'].queryset = Category.objects.filter(owner=request.user)
            context['adminform'].form.fields['usage'].queryset = Usage.objects.filter(user=request.user)
        return super().render_change_form(request, context, *args, **kwargs)