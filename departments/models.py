from django.db import models


class Department(models.Model):
    """Отдел компании"""

    name = models.CharField(
        'Название отдела',
        max_length=100,
        unique=True
    )

    code = models.CharField(
        'Код отдела',
        max_length=20,
        blank=True,
        help_text='Внутренний код (необязательно)'
    )

    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Вышестоящий отдел',
        related_name='child_departments'
    )

    is_active = models.BooleanField(
        'Активен',
        default=True
    )

    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'
        ordering = ['name']

    def __str__(self):
        return self.name
