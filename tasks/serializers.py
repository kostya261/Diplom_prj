from rest_framework import serializers
from .models import Task, TaskComment, TaskStatusLog


class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class TaskStatusLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model = TaskStatusLog
        fields = '__all__'
        read_only_fields = ['changed_at']


class TaskSerializer(serializers.ModelSerializer):
    responsible_name = serializers.CharField(source='responsible.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    parent_task_title = serializers.CharField(source='parent_task.title', read_only=True)

    # Вложенные списки
    comments = TaskCommentSerializer(many=True, read_only=True)
    status_logs = TaskStatusLogSerializer(many=True, read_only=True)

    # Соисполнители (ManyToMany)
    co_executors_names = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']

    def get_co_executors_names(self, obj):
        return [user.get_full_name() or user.username for user in obj.co_executors.all()]
