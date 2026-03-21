from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

from departments.models import Department


class User(AbstractUser):
    """Сотрудник = пользователь системы"""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер'
        EMPLOYEE = 'employee', 'Сотрудник'

    # Роль
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    # Телефон (обязательный)
    phone_regex = RegexValidator(
        regex=r'^\+?7?\d{10,15}$',
        message="Телефон должен быть в формате: '+71234567890'. Допускается до 15 цифр."
    )
    phone = models.CharField(
        'Телефон',
        validators=[phone_regex],
        max_length=16,
        blank=True,
        null=True,
        help_text="Формат: +71234567890"
    )

    # Email
    email = models.EmailField(
        'Email',
        blank=False,
        help_text="Обязательное поле"
    )

    # Паспортные данные
    passport_series = models.CharField(
        'Серия паспорта',
        max_length=10,
        blank=True,
        null=True,
        help_text="Формат: 1234 или 12 34"
    )
    passport_number = models.CharField(
        'Номер паспорта',
        max_length=10,
        blank=True,
        null=True,
        help_text="Формат: 123456"
    )
    passport_issued_by = models.CharField(
        'Кем выдан',
        max_length=255,
        blank=True,
        null=True
    )
    passport_issued_date = models.DateField(
        'Дата выдачи',
        null=True,
        blank=True
    )
    passport_code = models.CharField(
        'Код подразделения',
        max_length=10,
        blank=True,
        null=True,
        help_text="Формат: 123-456"
    )

    # Адрес
    registration_address = models.TextField(
        'Адрес регистрации',
        max_length=500,
        blank=True,
        null=True
    )
    residential_address = models.TextField(
        'Адрес проживания',
        max_length=500,
        blank=True,
        null=True,
        help_text="Если отличается от регистрации"
    )

    # Должность и отдел
    position = models.CharField(
        'Должность',
        max_length=255,
        blank=True,
        null=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Отдел',
        related_name='employees'
    )

    # Комментарий
    notes = models.TextField(
        'Заметки',
        blank=True,
        null=True,
        help_text="Дополнительная информация о сотруднике"
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.phone})"
        return f"{self.username} ({self.phone})"

    def save(self, *args, **kwargs):
        # Если email не заполнен, но есть username
        if not self.email and self.username:
            self.email = self.username
        super().save(*args, **kwargs)
