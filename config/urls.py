"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from departments.views import DepartmentViewSet
from users.views import UserViewSet
from . import views

# Настройка Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="TaskTracker API",
        default_version='v1',
        description="API для дипломного проекта - Трекер задач, Инструмент, Склад",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your.email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    # WEB
    path('', views.index, name='home'),
    path('employees/', include('users.urls_web')),
    path('tasks/', include('tasks.urls_web')),
    path('inventory/', include('inventory.urls_web')),
    path('warehouse/', include('warehouse.urls_web')),
    path('reports/employee-load/', views.employee_load_report, name='employee_load_report'),
    path('reports/important-tasks/', views.important_tasks_report, name='important_tasks_report'),

    # API
    path('api/', include(router.urls)),
    path('api/inventory/', include('inventory.urls')),
    path('api/warehouse/', include('warehouse.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
