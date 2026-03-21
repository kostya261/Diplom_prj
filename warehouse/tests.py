from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ProductCategory, ProductManufacturer, Product, StockMovement
from tasks.models import Task
from datetime import date, timedelta

User = get_user_model()


class WarehouseTests(APITestCase):
    """Тесты для складского учёта"""

    def setUp(self):
        """Создаём тестовых пользователей и объекты"""
        # Админ
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            phone='+71111111111',
            role='admin',
            first_name='Admin',
            last_name='Adminov'
        )

        # Менеджер
        self.manager = User.objects.create_user(
            username='manager',
            password='manager123',
            email='manager@test.com',
            phone='+72222222222',
            role='manager',
            first_name='Manager',
            last_name='Managerov'
        )

        # Обычный сотрудник
        self.employee = User.objects.create_user(
            username='employee',
            password='employee123',
            email='employee@test.com',
            phone='+73333333333',
            role='employee',
            first_name='Employee',
            last_name='Employeov'
        )

        # Категория
        self.category = ProductCategory.objects.create(
            name='Электроника',
            is_active=True
        )

        # Подкатегория
        self.subcategory = ProductCategory.objects.create(
            name='Провода',
            parent_category=self.category,
            is_active=True
        )

        # Производитель
        self.manufacturer = ProductManufacturer.objects.create(
            name='ТестПроизводитель',
            country='Россия',
            is_active=True
        )

        # Товар
        self.product = Product.objects.create(
            article='ART-001',
            name='Тестовый товар',
            category=self.subcategory,
            manufacturer=self.manufacturer,
            quantity=100,
            unit='шт',
            min_quantity=10,
            is_active=True
        )

        # Задача (для движений)
        self.task = Task.objects.create(
            title='Тестовая задача',
            responsible=self.employee,
            created_by=self.manager,
            deadline=date.today() + timedelta(days=7)
        )

        # Движение (приход)
        self.movement = StockMovement.objects.create(
            product=self.product,
            movement_type=StockMovement.MovementType.INCOMING,
            quantity=50,
            created_by=self.admin,
            comment='Тестовый приход'
        )

        # URL-ы
        self.categories_url = reverse('productcategory-list')
        self.manufacturers_url = reverse('productmanufacturer-list')
        self.products_url = reverse('product-list')
        self.movements_url = reverse('stockmovement-list')

    # ========== PRODUCT CATEGORIES ==========

    def test_list_categories_authenticated(self):
        """Авторизованный может видеть категории"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_categories_unauthenticated(self):
        """Неавторизованный не может видеть категории"""
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_admin(self):
        """Админ может создать категорию"""
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Механика'}
        response = self.client.post(self.categories_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductCategory.objects.count(), 3)

    def test_create_category_employee(self):
        """Сотрудник НЕ может создать категорию"""
        self.client.force_authenticate(user=self.employee)
        data = {'name': 'Механика'}
        response = self.client.post(self.categories_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_full_path(self):
        """Проверка метода get_full_path"""
        self.assertEqual(self.subcategory.get_full_path(), 'Электроника → Провода')

    # ========== PRODUCT MANUFACTURERS ==========

    def test_list_manufacturers_authenticated(self):
        """Авторизованный может видеть производителей"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.manufacturers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_manufacturer_admin(self):
        """Админ может создать производителя"""
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Новый производитель', 'country': 'Китай'}
        response = self.client.post(self.manufacturers_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductManufacturer.objects.count(), 2)

    def test_create_manufacturer_employee(self):
        """Сотрудник НЕ может создать производителя"""
        self.client.force_authenticate(user=self.employee)
        data = {'name': 'Новый производитель'}
        response = self.client.post(self.manufacturers_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========== PRODUCTS ==========

    def test_list_products_authenticated(self):
        """Авторизованный может видеть товары"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product_admin(self):
        """Админ может создать товар"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'article': 'ART-002',
            'name': 'Новый товар',
            'category': self.category.id,
            'manufacturer': self.manufacturer.id,
            'quantity': 200,
            'unit': 'шт'
        }
        response = self.client.post(self.products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_employee(self):
        """Сотрудник НЕ может создать товар"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'article': 'ART-002',
            'name': 'Новый товар',
            'quantity': 200
        }
        response = self.client.post(self.products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_is_low_stock(self):
        """Проверка свойства is_low_stock"""
        self.product.quantity = 5
        self.product.min_quantity = 10
        self.assertTrue(self.product.is_low_stock)

        self.product.quantity = 15
        self.assertFalse(self.product.is_low_stock)

    # ========== STOCK MOVEMENTS ==========

    def test_list_movements_authenticated(self):
        """Авторизованный может видеть движения"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.movements_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_movement_admin(self):
        """Админ может создать движение"""
        self.client.force_authenticate(user=self.admin)
        initial_quantity = self.product.quantity

        data = {
            'product': self.product.id,
            'movement_type': 'incoming',
            'quantity': 30,
            'created_by': self.admin.id,
            'comment': 'Новый приход'
        }
        response = self.client.post(self.movements_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что количество товара увеличилось
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity + 30)

    def test_create_outgoing_movement(self):
        """Создание расхода уменьшает количество"""
        self.client.force_authenticate(user=self.admin)
        initial_quantity = self.product.quantity

        data = {
            'product': self.product.id,
            'movement_type': 'outgoing',
            'quantity': 20,
            'created_by': self.admin.id,
            'comment': 'Расход'
        }
        response = self.client.post(self.movements_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity - 20)

    def test_create_movement_with_task(self):
        """Движение может быть привязано к задаче"""
        self.client.force_authenticate(user=self.admin)

        # Проверим, что задача существует
        self.assertIsNotNone(self.task.id)

        data = {
            'product': self.product.id,
            'movement_type': 'outgoing',
            'quantity': 5,
            'task': self.task.id,
            'created_by': self.admin.id,
            'comment': 'На задачу'
        }
        response = self.client.post(self.movements_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        movement_id = response.data['id']
        movement = StockMovement.objects.get(id=movement_id)
        self.assertEqual(movement.task.id, self.task.id)

    def test_create_movement_employee(self):
        """Сотрудник НЕ может создать движение"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'product': self.product.id,
            'movement_type': 'incoming',
            'quantity': 10,
            'created_by': self.employee.id
        }
        response = self.client.post(self.movements_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
