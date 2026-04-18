from asgiref.sync import sync_to_async
from product.models import Product

@sync_to_async
def get_product(product_id: int):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None