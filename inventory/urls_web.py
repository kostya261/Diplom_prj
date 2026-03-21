from django.urls import path
from . import views_web

urlpatterns = [
    path('', views_web.tool_list, name='tool_list'),
    path('add/', views_web.tool_form, name='tool_add'),
    path('<int:tool_id>/edit/', views_web.tool_form, name='tool_edit'),

    # Категории
    path('categories/', views_web.category_list, name='category_list'),
    path('categories/add/', views_web.category_form, name='category_add'),
    path('categories/<int:category_id>/edit/', views_web.category_form, name='category_edit'),

    # Производители
    path('manufacturers/', views_web.manufacturer_list, name='manufacturer_list'),
    path('manufacturers/add/', views_web.manufacturer_form, name='manufacturer_add'),
    path('manufacturers/<int:manufacturer_id>/edit/', views_web.manufacturer_form, name='manufacturer_edit'),

    # Места хранения
    path('locations/', views_web.location_list, name='location_list'),
    path('locations/add/', views_web.location_form, name='location_add'),
    path('locations/<int:location_id>/edit/', views_web.location_form, name='location_edit'),

    # Выдачи
    path('issues/', views_web.issue_list, name='issue_list'),
    path('issues/add/', views_web.issue_form, name='issue_add'),
    path('issues/<int:issue_id>/edit/', views_web.issue_form, name='issue_edit'),
    path('issues/<int:issue_id>/return/', views_web.return_tool, name='return_tool'),

    path('<int:tool_id>/report/', views_web.tool_report, name='tool_report'),
    path('issues/<int:issue_id>/report/', views_web.issue_report, name='issue_report'),
    path('employee-tools/', views_web.employee_tools, name='employee_tools'),
]
