from django.contrib import admin
from django.utils.html import format_html
from .models import ProductCategory, ProductManufacturer, Product, StockMovement


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active',)
    autocomplete_fields = ('parent_category',)
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'parent_category', 'description')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )


@admin.register(ProductManufacturer)
class ProductManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website', 'is_active')
    list_filter = ('is_active', 'country')
    search_fields = ('name',)
    list_editable = ('is_active',)


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('movement_type', 'quantity', 'task', 'created_by', 'created_at', 'comment')
    raw_id_fields = ('task', 'created_by')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'article',
        'name',
        'category',
        'manufacturer',
        'quantity',
        'unit',
        'is_low_stock_status',
        'is_active'
    )
    list_filter = ('category', 'manufacturer', 'is_active')
    search_fields = ('article', 'name', 'barcode')
    list_editable = ('is_active',)
    readonly_fields = ('quantity', 'created_at', 'updated_at')
    raw_id_fields = ('category', 'manufacturer')
    fieldsets = (
        ('Основное', {
            'fields': ('article', 'name', 'description', 'category', 'manufacturer')
        }),
        ('Учёт', {
            'fields': ('quantity', 'unit', 'min_quantity', 'max_quantity', 'barcode')
        }),
        ('Цены', {
            'fields': ('purchase_price', 'selling_price'),
            'classes': ('collapse',)
        }),
        ('Хранение', {
            'fields': ('location', 'photo'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    inlines = [StockMovementInline]

    def is_low_stock_status(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red;">⚠️ Ниже min</span>')
        return format_html('<span style="color: green;">✓ Норма</span>')
    is_low_stock_status.short_description = 'Остаток'
    is_low_stock_status.admin_order_field = 'quantity'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'task', 'created_by', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('product__name', 'product__article', 'comment')
    raw_id_fields = ('product', 'task', 'created_by')
    readonly_fields = ('old_quantity', 'new_quantity', 'created_at')
    fieldsets = (
        ('Операция', {
            'fields': ('product', 'movement_type', 'quantity')
        }),
        ('Связи', {
            'fields': ('task', 'created_by', 'document_number')
        }),
        ('Инвентаризация', {
            'fields': ('old_quantity', 'new_quantity'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_at')
        }),
    )
