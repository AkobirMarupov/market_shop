from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel
from product.models import Category
from account.models import User



class Usage(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usages', verbose_name=_("Sotuvchi"))
    title = models.CharField(_("Guruh nomi"), max_length=255)

    class Meta:
        db_table = 'usage'
        verbose_name_plural = _("Usage")
        unique_together = ('user', 'title')
        ordering = ['-id']

    def __str__(self):
        return f"{self.title} ({self.user})"

class UsageLink(BaseModel):
    usage = models.ForeignKey(Usage, related_name='links', on_delete=models.CASCADE)
    link = models.URLField(_("Telegram havola"), max_length=500)
    is_paid = models.BooleanField(_("To'langan"), default=False)
    is_active = models.BooleanField(_("Faol"), default=True)

    def __str__(self):
        return self.link

class LinkConnect(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='connected_links')
    usage = models.ForeignKey(Usage, on_delete=models.CASCADE, related_name='connected_categories')

    class Meta:
        unique_together = ('category', 'usage')

    def __str__(self):
        return f"{self.category.name} <-> {self.usage.title}"