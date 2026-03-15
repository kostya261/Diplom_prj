from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только для администраторов"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsManager(permissions.BasePermission):
    """Доступ для менеджеров и админов"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'manager']


class IsEmployee(permissions.BasePermission):
    """Доступ только для сотрудников (для ограничения)"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'


class IsAdminOrManager(permissions.BasePermission):
    """Админ или менеджер"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'manager']


class IsOwnerOrAdmin(permissions.BasePermission):
    """Доступ только владельцу объекта или админу"""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True

        # Для задач проверяем, является ли пользователь ответственным или соисполнителем
        if hasattr(obj, 'responsible'):
            return obj.responsible == request.user or request.user in obj.co_executors.all()

        # Для других объектов (например, комментарий) проверяем авторство
        if hasattr(obj, 'author'):
            return obj.author == request.user

        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False
