from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models import StorageLocation
from .models import ProductCategory, ProductManufacturer, Product


User = get_user_model()


class WarehouseWebTests(TestCase):
    """Тесты для веб-интерфейса warehouse"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            password='test123',
            email='test@test.com',
            phone='+71111111111',
            role='admin'
        )
        self.client.login(username='test', password='test123')

        # Создаём тестовые данные
        self.category = ProductCategory.objects.create(name='Электроника')
        self.manufacturer = ProductManufacturer.objects.create(name='Samsung')
        self.location = StorageLocation.objects.create(name='Склад А')
        self.product = Product.objects.create(
            article='ART-001',
            name='Телевизор',
            category=self.category,
            manufacturer=self.manufacturer,
            location=self.location,
            quantity=10,
            unit='шт'
        )

    def test_product_list_page(self):
        """Главная страница склада открывается"""
        response = self.client.get('/warehouse/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Телевизор')

    def test_product_add_page(self):
        """Страница добавления товара открывается"""
        response = self.client.get('/warehouse/add/')
        self.assertEqual(response.status_code, 200)

    def test_product_edit_page(self):
        """Страница редактирования товара открывается"""
        response = self.client.get(f'/warehouse/{self.product.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Телевизор')

    def test_category_list_page(self):
        """Список категорий открывается"""
        response = self.client.get('/warehouse/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Электроника')

    def test_manufacturer_list_page(self):
        """Список производителей открывается"""
        response = self.client.get('/warehouse/manufacturers/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Samsung')

    def test_movement_list_page(self):
        """Список движений открывается"""
        response = self.client.get('/warehouse/movements/')
        self.assertEqual(response.status_code, 200)

    def test_movement_add_page(self):
        """Страница добавления движения открывается"""
        response = self.client.get('/warehouse/movements/add/')
        self.assertEqual(response.status_code, 200)

    def test_inventory_select_page(self):
        """Страница выбора склада для инвентаризации открывается"""
        response = self.client.get('/warehouse/inventory/select/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Выберите склад')
