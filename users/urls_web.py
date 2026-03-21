from django.urls import path
from . import views_web

urlpatterns = [
    path('', views_web.employee_list, name='employee_list'),
    path('add/', views_web.employee_form, name='employee_add'),
    path('<int:employee_id>/edit/', views_web.employee_form, name='employee_edit'),
    path('<int:employee_id>/', views_web.employee_detail, name='employee_detail'),
]
