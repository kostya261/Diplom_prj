from django.contrib import admin
from .models import Task, TaskStatusLog, TaskComment


class TaskStatusLogInline(admin.TabularInline):
    model = TaskStatusLog
    extra = 0
    readonly_fields = ('status', 'changed_at', 'changed_by', 'comment')
    can_delete = False


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'responsible', 'status', 'priority', 'deadline')
    list_filter = ('status', 'priority', 'responsible')
    search_fields = ('title', 'description')
    raw_id_fields = ('parent_task',)
    autocomplete_fields = ['responsible', 'created_by', 'parent_task']
    filter_horizontal = ('co_executors',)
    date_hierarchy = 'deadline'
    readonly_fields = ('started_at', 'completed_at', 'created_at', 'updated_at')
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Назначение', {
            'fields': ('responsible', 'co_executors', 'created_by')
        }),
        ('Связи и сроки', {
            'fields': ('parent_task', 'deadline', 'started_at', 'completed_at')
        }),
        ('Системное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [TaskStatusLogInline, TaskCommentInline]

    def get_readonly_fields(self, request, obj=None):
        """Если создаётся новая задача, поле created_by не показываем"""
        if not obj:  # создание
            return ['created_at', 'updated_at']
        return ['created_at', 'updated_at', 'created_by']

    def save_model(self, request, obj, form, change):
        """Автоматически проставляем created_by при создании"""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TaskStatusLog)
class TaskStatusLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'get_status_display', 'changed_at', 'changed_by')
    list_filter = ('status', 'changed_by')
    readonly_fields = ('task', 'status', 'changed_at', 'changed_by', 'comment')
    search_fields = ('task__title', 'comment')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('text', 'task__title')
    raw_id_fields = ('task', 'author')
