from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductCategory, ProductManufacturer, Product, StockMovement
from .serializers import (
    ProductCategorySerializer, ProductManufacturerSerializer,
    ProductSerializer, StockMovementSerializer
)
from config.permissions import IsAdminOrManager


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class ProductManufacturerViewSet(viewsets.ModelViewSet):
    queryset = ProductManufacturer.objects.all()
    serializer_class = ProductManufacturerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'manufacturer', 'is_active']
    search_fields = ['article', 'name', 'barcode']
    ordering_fields = ['name', 'quantity', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'movement_type', 'task', 'created_by']
    search_fields = ['product__name', 'comment', 'document_number']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
