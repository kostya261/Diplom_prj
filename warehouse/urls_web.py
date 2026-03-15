from django.urls import path
from . import views_web

urlpatterns = [
    path('add/', views_web.product_form, name='product_add'),
    path('<int:product_id>/edit/', views_web.product_form, name='product_edit'),
    path('movements/add/', views_web.movement_form, name='movement_add'),
    path('movements/', views_web.movement_list, name='movement_list'),
    path('', views_web.product_list, name='product_list'),

    # Категории товаров
    path('categories/', views_web.category_list, name='warehouse_category_list'),
    path('categories/add/', views_web.category_form, name='warehouse_category_add'),
    path('categories/<int:category_id>/edit/', views_web.category_form, name='warehouse_category_edit'),

    # Производители товаров
    path('manufacturers/', views_web.manufacturer_list, name='warehouse_manufacturer_list'),
    path('manufacturers/add/', views_web.manufacturer_form, name='warehouse_manufacturer_add'),
    path('manufacturers/<int:manufacturer_id>/edit/', views_web.manufacturer_form, name='warehouse_manufacturer_edit'),

    path('reports/stock-balance/', views_web.report_stock_balance, name='report_stock_balance'),
    path('reports/inventory/', views_web.report_inventory, name='report_inventory'),
    path('inventory/select/', views_web.report_inventory, name='inventory_select'),
    path('movements/<int:movement_id>/incoming/', views_web.report_incoming, name='report_incoming'),
    path('movements/<int:movement_id>/outgoing/', views_web.report_outgoing, name='report_outgoing'),
    path('transfer/', views_web.transfer_product, name='transfer_product'),
]
