from django.urls import path
from . import views_web

urlpatterns = [
    path('', views_web.task_list, name='task_list'),
    path('add/', views_web.task_form, name='task_add'),
    path('<int:task_id>/edit/', views_web.task_form, name='task_edit'),
    path('<int:task_id>/report/', views_web.report_task_order, name='report_task_order'),
    path('<int:task_id>/order/', views_web.task_order, name='task_order'),
    path('<int:task_id>/status/<str:new_status>/', views_web.change_task_status, name='change_task_status'),
]
