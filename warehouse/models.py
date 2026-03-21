from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from tasks.models import Task


class ProductCategory(models.Model):
    """Категория товара (только иерархия, без производителя)"""

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
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'
        unique_together = ['name', 'parent_category']
        ordering = ['name']

    def __str__(self):
        return self.get_full_path()

    def get_full_path(self):
        """Полный путь категории (например: Ворота → Откатные → Came)"""
        path = [self.name]
        parent = self.parent_category
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent_category
        return ' → '.join(path)


class ProductManufacturer(models.Model):
    """Производитель товаров/запчастей"""

    name = models.CharField(
        'Название производителя',
        max_length=100,
        unique=True
    )

    description = models.TextField(
        'Описание',
        blank=True,
        help_text='Краткая информация о производителе'
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
        verbose_name = 'Производитель товаров'
        verbose_name_plural = 'Производители товаров'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар/запчасть на складе"""

    # Основное
    article = models.CharField(
        'Артикул',
        max_length=50,
        unique=True,
        help_text='Уникальный артикул товара'
    )

    name = models.CharField(
        'Наименование',
        max_length=255
    )

    description = models.TextField(
        'Описание',
        blank=True
    )

    # Связи
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
        related_name='products'
    )

    manufacturer = models.ForeignKey(
        ProductManufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Производитель',
        related_name='products'
    )

    # Учёт
    quantity = models.DecimalField(
        'Текущий остаток',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Текущее количество на складе'
    )

    unit = models.CharField(
        'Единица измерения',
        max_length=20,
        default='шт',
        help_text='шт, м, кг, компл, упак и т.д.'
    )

    min_quantity = models.DecimalField(
        'Минимальный остаток',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='При достижении этого значения рекомендуется заказ'
    )

    max_quantity = models.DecimalField(
        'Максимальный остаток',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Желаемый максимум (для планирования закупок)'
    )

    # Цены
    purchase_price = models.DecimalField(
        'Закупочная цена',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Цена за единицу при закупке'
    )

    selling_price = models.DecimalField(
        'Цена списания',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Цена при списании на задачи'
    )

    # Хранение
    location = models.ForeignKey(
        'inventory.StorageLocation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Место хранения',
        related_name='warehouse_products',
        help_text='Где товар находится'
    )

    barcode = models.CharField(
        'Штрихкод',
        max_length=100,
        blank=True,
        help_text='Штрихкод товара (EAN-13 и т.п.)'
    )

    # Фото
    photo = models.ImageField(
        'Фото',
        upload_to='products/%Y/%m/',
        blank=True,
        null=True
    )

    # Статус
    is_active = models.BooleanField(
        'Активен',
        default=True,
        help_text='Снимать с учёта, если не используется'
    )

    # Мета
    created_at = models.DateTimeField(
        'Добавлен',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        'Обновлён',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.article} - {self.name}"

    @property
    def is_low_stock(self):
        """Проверка, не ниже ли остаток минимального уровня"""
        return self.quantity <= self.min_quantity


class StockMovement(models.Model):
    """Движение товара (приход, расход, списание, инвентаризация)"""

    class MovementType(models.TextChoices):
        INCOMING = 'incoming', 'Приход'
        OUTGOING = 'outgoing', 'Расход'
        WRITE_OFF = 'write_off', 'Списание'
        INVENTORY = 'inventory', 'Инвентаризация'
        RETURN = 'return', 'Возврат'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Товар'
    )

    movement_type = models.CharField(
        'Тип движения',
        max_length=20,
        choices=MovementType.choices
    )

    quantity = models.DecimalField(
        'Количество',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Количество (всегда положительное)'
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Задача',
        related_name='stock_movements',
        help_text='Если расход связан с конкретной задачей'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Ответственный',
        related_name='stock_movements'
    )

    document_number = models.CharField(
        'Номер документа',
        max_length=50,
        blank=True,
        help_text='Номер накладной, акта и т.п.'
    )

    comment = models.TextField(
        'Комментарий',
        blank=True,
        help_text='Причина, особые отметки'
    )

    old_quantity = models.DecimalField(
        'Старый остаток',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Для инвентаризации'
    )

    new_quantity = models.DecimalField(
        'Новый остаток',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Для инвентаризации'
    )

    created_at = models.DateTimeField(
        'Дата операции',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Движение товара'
        verbose_name_plural = 'Движения товаров'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.product} {self.quantity} ({self.created_at})"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.movement_type == self.MovementType.INCOMING:
                self.product.quantity += self.quantity
            elif self.movement_type in [self.MovementType.OUTGOING, self.MovementType.WRITE_OFF]:
                self.product.quantity -= self.quantity
            elif self.movement_type == self.MovementType.RETURN:
                self.product.quantity += self.quantity
            elif self.movement_type == self.MovementType.INVENTORY:
                self.old_quantity = self.product.quantity
                if self.new_quantity is not None:
                    self.product.quantity = self.new_quantity
            self.product.save()
        super().save(*args, **kwargs)
