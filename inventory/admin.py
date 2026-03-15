from django.contrib import admin
from .models import StorageLocation, ToolCategory, ToolManufacturer, Tool, ToolIssue


@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location_type', 'parent_location', 'is_active')
    list_filter = ('location_type', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_editable = ('is_active',)
    autocomplete_fields = ('parent_location',)
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'code', 'location_type', 'parent_location')
        }),
        ('Дополнительно', {
            'fields': ('description', 'is_active')
        }),
    )


@admin.register(ToolCategory)
class ToolCategoryAdmin(admin.ModelAdmin):
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


@admin.register(ToolManufacturer)
class ToolManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website', 'is_active')
    list_filter = ('is_active', 'country')
    search_fields = ('name',)
    list_editable = ('is_active',)


class ToolIssueInline(admin.TabularInline):
    model = ToolIssue
    extra = 0
    readonly_fields = ('issued_at', 'returned_at')
    fields = ('issued_to', 'issued_by', 'issued_at', 'expected_return_at', 'returned_at', 'notes')
    raw_id_fields = ('issued_to', 'issued_by', 'returned_to')


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'inventory_number', 'category', 'manufacturer', 'status', 'location')
    list_filter = ('status', 'category', 'manufacturer')
    search_fields = ('name', 'inventory_number', 'serial_number')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('category', 'manufacturer', 'location')
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'inventory_number', 'serial_number', 'category', 'manufacturer', 'status')
        }),
        ('Характеристики', {
            'fields': ('model', 'year_of_manufacture'),
            'classes': ('collapse',)
        }),
        ('Учёт', {
            'fields': ('location', 'purchase_date', 'purchase_cost'),
            'classes': ('collapse',)
        }),
        ('Техническое состояние', {
            'fields': ('condition', 'photo')
        }),
        ('Системное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ToolIssueInline]


@admin.register(ToolIssue)
class ToolIssueAdmin(admin.ModelAdmin):
    list_display = ('tool', 'issued_to', 'issued_at', 'returned_at')
    list_filter = ('issued_at', 'returned_at')
    search_fields = ('tool__name', 'issued_to__username', 'issued_to__email')
    readonly_fields = ('issued_at',)
    raw_id_fields = ('tool', 'issued_to', 'issued_by', 'returned_to')
    autocomplete_fields = ('tool', 'issued_to', 'issued_by', 'returned_to')
    fieldsets = (
        ('Выдача', {
            'fields': ('tool', 'issued_to', 'issued_by', 'issued_at', 'expected_return_at')
        }),
        ('Возврат', {
            'fields': ('returned_at', 'returned_to', 'notes')
        }),
    )
