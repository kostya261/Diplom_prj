from django.db import models
from django.utils import timezone
from users.models import User


class StorageLocation(models.Model):
    """Место хранения (склад, стеллаж, ячейка)"""

    name = models.CharField(
        'Название',
        max_length=100,
        help_text='Например: Склад №1, Стеллаж А, Ячейка 12'
    )

    code = models.CharField(
        'Код',
        max_length=50,
        blank=True,
        help_text='Внутренний код или штрихкод места'
    )

    description = models.TextField(
        'Описание',
        blank=True,
        help_text='Дополнительная информация о месте хранения'
    )

    parent_location = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Входит в',
        related_name='sublocations',
        help_text='Например, ячейка может входить в стеллаж'
    )

    location_type = models.CharField(
        'Тип места',
        max_length=50,
        choices=[
            ('warehouse', 'Склад'),
            ('rack', 'Стеллаж'),
            ('shelf', 'Полка'),
            ('cell', 'Ячейка'),
            ('other', 'Другое'),
        ],
        default='warehouse'
    )

    is_active = models.BooleanField(
        'Активно',
        default=True
    )

    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Место хранения'
        verbose_name_plural = 'Места хранения'
        ordering = ['name']
        unique_together = ['name', 'parent_location']

    def __str__(self):
        if self.parent_location:
            return f"{self.parent_location} → {self.name}"
        return self.name

    def get_full_path(self):
        path = [self.name]
        parent = self.parent_location
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent_location
        return ' → '.join(path)


class ToolCategory(models.Model):
    """Категория инструмента (только иерархия)"""

    name = models.CharField(
        'Название категории',
        max_length=100
    )

    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Родительская категория',
        related_name='subcategories'
    )

    description = models.TextField(
        'Описание',
        blank=True
    )

    is_active = models.BooleanField(
        'Активна',
        default=True
    )

    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Категория инструмента'
        verbose_name_plural = 'Категории инструментов'
        unique_together = ['name', 'parent_category']
        ordering = ['name']

    def __str__(self):
        return self.get_full_path()

    def get_full_path(self):
        path = [self.name]
        parent = self.parent_category
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent_category
        return ' → '.join(path)


class ToolManufacturer(models.Model):
    """Производитель инструмента"""

    name = models.CharField(
        'Название производителя',
        max_length=100,
        unique=True
    )

    description = models.TextField(
        'Описание',
        blank=True
    )

    website = models.URLField(
        'Сайт',
        blank=True
    )

    country = models.CharField(
        'Страна',
        max_length=100,
        blank=True
    )

    is_active = models.BooleanField(
        'Активен',
        default=True
    )

    created_at = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Производитель инструмента'
        verbose_name_plural = 'Производители инструмента'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tool(models.Model):
    """Инструмент/оборудование"""

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Доступен'
        IN_USE = 'in_use', 'Выдан'
        MAINTENANCE = 'maintenance', 'На обслуживании'
        WRITE_OFF = 'write_off', 'Списан'

    name = models.CharField(
        'Наименование',
        max_length=255
    )

    inventory_number = models.CharField(
        'Инвентарный номер',
        max_length=50,
        unique=True,
        help_text='Уникальный номер в системе учёта'
    )

    serial_number = models.CharField(
        'Серийный номер',
        max_length=100,
        blank=True,
        help_text='Заводской номер'
    )

    category = models.ForeignKey(
        ToolCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
        related_name='tools'
    )

    manufacturer = models.ForeignKey(
        ToolManufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Производитель',
        related_name='tools'
    )

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )

    location = models.ForeignKey(
        StorageLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Место хранения',
        related_name='tools',
        help_text='Где инструмент находится'
    )

    model = models.CharField(
        'Модель',
        max_length=100,
        blank=True,
        help_text='Модель инструмента'
    )

    year_of_manufacture = models.IntegerField(
        'Год выпуска',
        null=True,
        blank=True
    )

    purchase_date = models.DateField(
        'Дата приобретения',
        null=True,
        blank=True
    )

    purchase_cost = models.DecimalField(
        'Стоимость',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    condition = models.TextField(
        'Техническое состояние',
        blank=True,
        help_text='Заметки о состоянии, дефектах'
    )

    photo = models.ImageField(
        'Фото',
        upload_to='tools/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        'Добавлен',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        'Обновлён',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Инструмент'
        verbose_name_plural = 'Инструменты'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.inventory_number})"

    def is_available(self):
        return self.status == self.Status.AVAILABLE


class ToolIssue(models.Model):
    """Выдача инструмента"""

    tool = models.ForeignKey(
        Tool,
        on_delete=models.CASCADE,
        related_name='issues',
        verbose_name='Инструмент'
    )

    issued_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tools_taken',
        verbose_name='Кому выдан'
    )

    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tools_issued',
        verbose_name='Кто выдал'
    )

    issued_at = models.DateTimeField(
        'Время выдачи',
        auto_now_add=True
    )

    expected_return_at = models.DateTimeField(
        'Ожидаемое возвращение',
        null=True,
        blank=True
    )

    returned_at = models.DateTimeField(
        'Время возврата',
        null=True,
        blank=True
    )

    returned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tools_received_back',
        verbose_name='Кто принял'
    )

    notes = models.TextField(
        'Примечания',
        blank=True,
        help_text='Состояние при выдаче/возврате, особые отметки'
    )

    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Задача',
        related_name='tool_issues'
    )

    class Meta:
        verbose_name = 'Выдача инструмента'
        verbose_name_plural = 'Выдачи инструмента'
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.tool} -> {self.issued_to} в {self.issued_at}"

    def return_tool(self, returned_by, notes=''):
        self.returned_at = timezone.now()
        self.returned_to = returned_by
        if notes:
            self.notes += f"\nПри возврате: {notes}"
        self.save()
        self.tool.status = Tool.Status.AVAILABLE
        self.tool.save()
