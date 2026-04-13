from rest_framework import serializers
from product.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'price', 
            'image', 'description', 'telegram_message_id'
        ]

    def validate_category(self, value):
        request = self.context.get('request')
        if value.owner != request.user:
            raise serializers.ValidationError("Bu kategoriya sizga tegishli emas!")
        return value