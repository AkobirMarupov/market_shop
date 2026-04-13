from rest_framework import serializers
from product.models import Category


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'products_count', 'children']
        extra_kwargs = {
            'parent': {'write_only': True}
        }

    def get_products_count(self, obj):
        return obj.products.count()

    def get_children(self, obj):
        serializer = CategorySerializer(obj.children.all(), many=True, context=self.context)
        return serializer.data

    def validate(self, attrs):
        request = self.context.get('request')
        name = attrs.get('name')
        parent = attrs.get('parent')

        if request and request.user:
            user = request.user
            
            qs = Category.objects.filter(owner=user, name__iexact=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError({"name": f"Sizda allaqachon '{name}' nomli kategoriya mavjud."})

            # 2. Ota kategoriya xavfsizligi
            if parent and parent.owner != user:
                raise serializers.ValidationError({"parent": "Boshqa foydalanuvchining kategoriyasiga bog'lay olmaysiz!"})
                
        return attrs