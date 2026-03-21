from rest_framework import viewsets, permissions, filters
from .models import Department
from .serializers import DepartmentSerializer
from config.permissions import IsAdminOrManager


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с отделами.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name']

    def get_permissions(self):
        """
        Права доступа:
        - Список и детали могут смотреть все авторизованные
        - Создание, изменение, удаление — только админы и менеджеры
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
