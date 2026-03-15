from django.db import models
from django.utils import timezone
from users.models import User


class Task(models.Model):
    """Задача"""

    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'В работе'
        ON_HOLD = 'on_hold', 'На паузе'
        DONE = 'done', 'Завершена'

    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'
        CRITICAL = 'critical', 'Критический'

    # Основные поля
    title = models.CharField(
        'Наименование',
        max_length=500
    )
    description = models.TextField(
        'Описание',
        blank=True
    )

    # Связи
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Родительская задача',
        related_name='subtasks'
    )

    # Ответственный (один, обязательный)
    responsible = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='responsible_tasks',
        verbose_name='Ответственный'
    )

    # Соисполнители (много, необязательно)
    co_executors = models.ManyToManyField(
        User,
        blank=True,
        related_name='co_tasks',
        verbose_name='Соисполнители'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name='Кто создал'
    )

    # Атрибуты
    priority = models.CharField(
        'Приоритет',
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    deadline = models.DateField(
        'Срок выполнения'
    )

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )

    # Даты выполнения
    started_at = models.DateTimeField(
        'Начало выполнения',
        null=True,
        blank=True,
        help_text='Когда задача фактически начата'
    )

    completed_at = models.DateTimeField(
        'Окончание выполнения',
        null=True,
        blank=True,
        help_text='Когда задача фактически завершена'
    )

    # Мета
    created_at = models.DateTimeField(
        'Создана',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Обновлена',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_all_executors(self):
        """Возвращает список всех исполнителей (ответственный + соисполнители)"""
        executors = [self.responsible] if self.responsible else []
        executors.extend(self.co_executors.all())
        return executors

    def change_status(self, new_status, user=None, comment=''):
        """Сменить статус задачи с логированием"""
        if self.status != new_status:
            self.status = new_status
            self.save()

            # Создаём запись в логе
            TaskStatusLog.objects.create(
                task=self,
                status=new_status,
                changed_by=user,
                comment=comment
            )

            # Если статус DONE - ставим completed_at
            if new_status == self.Status.DONE and not self.completed_at:
                self.completed_at = timezone.now()
                self.save()

            # Если статус IN_PROGRESS и нет started_at
            if new_status == self.Status.IN_PROGRESS and not self.started_at:
                self.started_at = timezone.now()
                self.save()

            return True
        return False


class TaskStatusLog(models.Model):
    """Лог изменений статуса задачи"""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name='Задача'
    )

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Task.Status.choices
    )

    changed_at = models.DateTimeField(
        'Время изменения',
        auto_now_add=True
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Кто изменил'
    )

    comment = models.CharField(
        'Комментарий к изменению',
        max_length=255,
        blank=True,
        help_text='Например: "Приступил", "Отложил", "Завершил"'
    )

    class Meta:
        verbose_name = 'Лог статуса'
        verbose_name_plural = 'Логи статусов'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.task} -> {self.get_status_display()} в {self.changed_at}"


class TaskComment(models.Model):
    """Комментарий к задаче"""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Задача'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    text = models.TextField(
        'Текст комментария'
    )

    created_at = models.DateTimeField(
        'Создан',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Изменён',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author}: {self.text[:50]}..."
