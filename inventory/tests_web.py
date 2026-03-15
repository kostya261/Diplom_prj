from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ToolCategory, ToolManufacturer, StorageLocation, Tool

User = get_user_model()


class InventoryWebTests(TestCase):
    """Тесты для веб-интерфейса inventory"""

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
        self.category = ToolCategory.objects.create(name='Дрели')
        self.manufacturer = ToolManufacturer.objects.create(name='Bosch')
        self.location = StorageLocation.objects.create(name='Склад №1')
        self.tool = Tool.objects.create(
            name='Дрель',
            inventory_number='INV-001',
            category=self.category,
            manufacturer=self.manufacturer,
            location=self.location
        )

    def test_tool_list_page(self):
        """Главная страница инструмента открывается"""
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дрель')

    def test_tool_add_page(self):
        """Страница добавления инструмента открывается"""
        response = self.client.get('/inventory/add/')
        self.assertEqual(response.status_code, 200)

    def test_tool_edit_page(self):
        """Страница редактирования инструмента открывается"""
        response = self.client.get(f'/inventory/{self.tool.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дрель')

    def test_category_list_page(self):
        """Список категорий открывается"""
        response = self.client.get('/inventory/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дрели')

    def test_category_add_page(self):
        """Страница добавления категории открывается"""
        response = self.client.get('/inventory/categories/add/')
        self.assertEqual(response.status_code, 200)

    def test_manufacturer_list_page(self):
        """Список производителей открывается"""
        response = self.client.get('/inventory/manufacturers/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bosch')

    def test_location_list_page(self):
        """Список мест хранения открывается"""
        response = self.client.get('/inventory/locations/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Склад №1')

    def test_issue_list_page(self):
        """Список выдач открывается"""
        response = self.client.get('/inventory/issues/')
        self.assertEqual(response.status_code, 200)
