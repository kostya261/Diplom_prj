from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Task, TaskComment, TaskStatusLog
from .serializers import TaskSerializer, TaskCommentSerializer, TaskStatusLogSerializer
from config.permissions import IsAdminOrManager


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'responsible', 'parent_task']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'priority']

    def get_permissions(self):
        """
        Разные права для разных действий
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Создавать, изменять, удалять задачи могут только админы и менеджеры
            permission_classes = [IsAdminOrManager]
        elif self.action in ['employee_load', 'important_tasks']:
            # Спецэндпоинты — только для админов и менеджеров
            permission_classes = [IsAdminOrManager]
        elif self.action in ['change_status', 'add_comment']:
            # Менять статус и комментировать могут все аутентифицированные
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Сотрудники видят только свои задачи, админы/менеджеры - всё"""
        user = self.request.user
        if user.role == 'employee':
            return Task.objects.filter(
                Q(responsible=user) | Q(co_executors=user)
            ).distinct()
        return Task.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Смена статуса задачи с логированием"""
        task = self.get_object()

        # Дополнительная проверка для сотрудников
        if request.user.role == 'employee':
            if task.responsible != request.user and request.user not in task.co_executors.all():
                return Response(
                    {'error': 'Вы можете менять статус только своих задач'},
                    status=status.HTTP_403_FORBIDDEN
                )

        new_status = request.data.get('status')
        comment = request.data.get('comment', '')

        if not new_status:
            return Response(
                {'error': 'Не указан статус'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if task.change_status(new_status, request.user, comment):
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Статус не изменился или недопустим'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Добавить комментарий к задаче"""
        task = self.get_object()

        # Дополнительная проверка для сотрудников
        if request.user.role == 'employee':
            if task.responsible != request.user and request.user not in task.co_executors.all():
                return Response(
                    {'error': 'Вы можете комментировать только свои задачи'},
                    status=status.HTTP_403_FORBIDDEN
                )

        text = request.data.get('text')

        if not text:
            return Response(
                {'error': 'Текст комментария не может быть пустым'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = TaskComment.objects.create(
            task=task,
            author=request.user,
            text=text
        )

        serializer = TaskCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def employee_load(self, request):
        """
        Спецэндпоинт 1: Занятые сотрудники
        """
        from users.models import User
        from django.db.models import Count

        employees = User.objects.annotate(
            active_tasks=Count(
                'responsible_tasks',
                filter=~Q(responsible_tasks__status='done')
            ) + Count(
                'co_tasks',
                filter=~Q(co_tasks__status='done')
            )
        ).filter(
            Q(role='employee') | Q(role='manager')
        ).order_by('-active_tasks')

        data = [
            {
                'id': emp.id,
                'full_name': emp.get_full_name() or emp.username,
                'position': emp.position,
                'department': emp.department.name if emp.department else None,
                'active_tasks': emp.active_tasks
            }
            for emp in employees
        ]

        return Response(data)

    @action(detail=False, methods=['get'])
    def important_tasks(self, request):
        """
        Спецэндпоинт 2: Важные задачи
        """
        important_tasks = Task.objects.filter(
            status='new',
            subtasks__status='in_progress'
        ).distinct()

        result = []

        for task in important_tasks:
            parent_executor = None
            if task.parent_task and task.parent_task.responsible:
                parent_executor = task.parent_task.responsible

            from users.models import User
            from django.db.models import Count

            all_employees = User.objects.annotate(
                active_tasks=Count(
                    'responsible_tasks',
                    filter=~Q(responsible_tasks__status='done')
                ) + Count(
                    'co_tasks',
                    filter=~Q(co_tasks__status='done')
                )
            ).filter(role__in=['employee', 'manager']).order_by('active_tasks')

            least_loaded = all_employees.first()
            candidate = None

            if parent_executor:
                parent_load = all_employees.get(id=parent_executor.id).active_tasks
                least_load = least_loaded.active_tasks if least_loaded else 0
                if parent_load <= least_load + 2:
                    candidate = parent_executor

            if not candidate:
                candidate = least_loaded

            if candidate:
                result.append({
                    'task': task.title,
                    'deadline': task.deadline,
                    'candidate': candidate.get_full_name() or candidate.username
                })

        return Response(result)


class TaskCommentViewSet(viewsets.ModelViewSet):
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task', 'author']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrManager]  # только админы/менеджеры могут удалять/править чужие комментарии
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Сотрудники видят только комментарии к своим задачам"""
        user = self.request.user
        if user.role == 'employee':
            return TaskComment.objects.filter(
                Q(task__responsible=user) | Q(task__co_executors=user)
            ).distinct()
        return TaskComment.objects.all()


class TaskStatusLogViewSet(viewsets.ModelViewSet):
    queryset = TaskStatusLog.objects.all()
    serializer_class = TaskStatusLogSerializer
    permission_classes = [IsAdminOrManager]  # только админы и менеджеры могут смотреть логи
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task', 'status', 'changed_by']
    ordering_fields = ['changed_at']
