from rest_framework.routers import DefaultRouter
from .views import (
    ToolCategoryViewSet, ToolManufacturerViewSet,
    ToolViewSet, ToolIssueViewSet, StorageLocationViewSet
)

router = DefaultRouter()
router.register(r'categories', ToolCategoryViewSet)
router.register(r'manufacturers', ToolManufacturerViewSet)
router.register(r'tools', ToolViewSet)
router.register(r'issues', ToolIssueViewSet)
router.register(r'locations', StorageLocationViewSet)

urlpatterns = router.urls
