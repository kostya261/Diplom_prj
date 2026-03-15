from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet, ProductManufacturerViewSet,
    ProductViewSet, StockMovementViewSet
)

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet)
router.register(r'manufacturers', ProductManufacturerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'movements', StockMovementViewSet)

urlpatterns = router.urls
