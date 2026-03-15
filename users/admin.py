from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'position')
    list_filter = ('role', 'department')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {
            'fields': (
                'role', 'phone', 'position', 'department',
                'passport_series', 'passport_number', 'passport_issued_by',
                'passport_issued_date', 'passport_code',
                'registration_address', 'residential_address', 'notes'
            ),
        }),
    )
