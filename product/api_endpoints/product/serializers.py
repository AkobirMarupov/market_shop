from rest_framework import serializers
from product.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
                'id',
                'name',
                'category',
                'price',
                'brand',
                'size',
                'color',
                'material',
                'currency',
                'telegram_message_id',
                'description',
                'image',
        ]

    def validate_category(self, value):
        request = self.context.get('request')
        if value.owner != request.user:
            raise serializers.ValidationError("Bu kategoriya sizga tegishli emas!")
        return value