from rest_framework import serializers
from usage.models import Usage, UsageLink, LinkConnect
from product.models import Product


class UsageLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageLink
        fields = ['id', 'usage', 'link', 'is_paid', 'is_active']
        read_only_fields = ['is_paid']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        usage = attrs.get('usage')

        if usage.user != user:
            raise serializers.ValidationError({"usage": "Sizga tegishli bo'lmagan guruhga link qo'sha olmaysiz!"})

        existing_links_count = UsageLink.objects.filter(usage__user=user).count()

        if existing_links_count >= 1:
            is_staff = getattr(user, 'is_staff', False)
            is_premium = getattr(user, 'is_premium', False)
            
            if not (is_staff or is_premium):
                raise serializers.ValidationError({
                    "premium_required": "Sizda bitta bepul havola mavjud. Yana link qo'shish uchun Premium sotib olishingiz kerak!"
                })

        return attrs

# 2. Usage Serializer (Guruhlar uchun)
class UsageSerializer(serializers.ModelSerializer):
    links = UsageLinkSerializer(many=True, read_only=True)
    links_count = serializers.SerializerMethodField()

    class Meta:
        model = Usage
        fields = ['id', 'title', 'links_count', 'links']

    def get_links_count(self, obj):
        return obj.links.count()

    def validate_title(self, value):
        request = self.context.get('request')
        if Usage.objects.filter(user=request.user, title__iexact=value).exists():
            raise serializers.ValidationError("Sizda bunday nomli guruh allaqachon mavjud!")
        return value

# 3. LinkConnect Serializer (Kategoriya va Guruhni bog'lash)
class LinkConnectSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkConnect
        fields = ['id', 'category', 'usage']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        category = attrs.get('category')
        usage = attrs.get('usage')

        if category.owner != user:
            raise serializers.ValidationError({"category": "Bu kategoriya sizniki emas!"})
        
        if usage.user != user:
            raise serializers.ValidationError({"usage": "Bu guruh sizniki emas!"})

        return attrs
    

class TelegramSyncSerializer(serializers.Serializer):
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="Yubormoqchi bo'lgan kategoriya IDlari ro'yxati"
    )