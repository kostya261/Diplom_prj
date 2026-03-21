from rest_framework import serializers
from .models import ProductCategory, ProductManufacturer, Product, StockMovement


class ProductCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source='get_full_path', read_only=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductManufacturer
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_full_path = serializers.CharField(source='category.get_full_path', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ['created_at']
