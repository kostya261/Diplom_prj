from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import StorageLocation, ToolCategory, ToolManufacturer, Tool, ToolIssue

User = get_user_model()


class InventoryTests(APITestCase):
    """Тесты для приложения inventory"""

    def setUp(self):
        """Создаём тестовых пользователей и объекты"""
        # Админ
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            phone='+71111111111',
            role='admin'
        )

        # Менеджер
        self.manager = User.objects.create_user(
            username='manager',
            password='manager123',
            email='manager@test.com',
            phone='+72222222222',
            role='manager'
        )

        # Обычный сотрудник
        self.employee = User.objects.create_user(
            username='employee',
            password='employee123',
            email='employee@test.com',
            phone='+73333333333',
            role='employee'
        )

        # Тестовые объекты
        self.location = StorageLocation.objects.create(
            name='Склад №1',
            location_type='warehouse',
            is_active=True
        )

        self.category = ToolCategory.objects.create(
            name='Электроинструмент',
            is_active=True
        )

        self.manufacturer = ToolManufacturer.objects.create(
            name='Bosch',
            country='Германия',
            is_active=True
        )

        self.tool = Tool.objects.create(
            name='Дрель',
            inventory_number='INV-001',
            serial_number='123456',
            category=self.category,
            manufacturer=self.manufacturer,
            status=Tool.Status.AVAILABLE,
            location=self.location
        )

        self.issue = ToolIssue.objects.create(
            tool=self.tool,
            issued_to=self.employee,
            issued_by=self.manager
        )

        # URL-ы
        self.locations_url = reverse('storagelocation-list')
        self.categories_url = reverse('toolcategory-list')
        self.manufacturers_url = reverse('toolmanufacturer-list')
        self.tools_url = reverse('tool-list')
        self.issues_url = reverse('toolissue-list')

    # ========== STORAGE LOCATIONS ==========

    def test_list_locations_authenticated(self):
        """Авторизованный может смотреть места хранения"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.locations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_locations_unauthenticated(self):
        """Неавторизованный не может смотреть места хранения"""
        response = self.client.get(self.locations_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_location_admin(self):
        """Админ может создать место хранения"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Стеллаж А',
            'location_type': 'rack',
            'is_active': True
        }
        response = self.client.post(self.locations_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StorageLocation.objects.count(), 2)

    def test_create_location_employee(self):
        """Сотрудник НЕ может создать место хранения"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'name': 'Стеллаж А',
            'location_type': 'rack',
            'is_active': True
        }
        response = self.client.post(self.locations_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========== TOOL CATEGORIES ==========

    def test_list_categories_authenticated(self):
        """Авторизованный может смотреть категории"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_admin(self):
        """Админ может создать категорию"""
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Ручной инструмент'}
        response = self.client.post(self.categories_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ToolCategory.objects.count(), 2)

    def test_create_category_employee(self):
        """Сотрудник НЕ может создать категорию"""
        self.client.force_authenticate(user=self.employee)
        data = {'name': 'Ручной инструмент'}
        response = self.client.post(self.categories_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========== TOOL MANUFACTURERS ==========

    def test_list_manufacturers_authenticated(self):
        """Авторизованный может смотреть производителей"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.manufacturers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_manufacturer_admin(self):
        """Админ может создать производителя"""
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Makita', 'country': 'Япония'}
        response = self.client.post(self.manufacturers_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ToolManufacturer.objects.count(), 2)

    def test_create_manufacturer_employee(self):
        """Сотрудник НЕ может создать производителя"""
        self.client.force_authenticate(user=self.employee)
        data = {'name': 'Makita', 'country': 'Япония'}
        response = self.client.post(self.manufacturers_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========== TOOLS ==========

    def test_list_tools_authenticated(self):
        """Авторизованный может смотреть инструменты"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.tools_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_tool_admin(self):
        """Админ может создать инструмент"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Болгарка',
            'inventory_number': 'INV-002',
            'category': self.category.id,
            'manufacturer': self.manufacturer.id,
            'status': 'available',
            'location': self.location.id
        }
        response = self.client.post(self.tools_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tool.objects.count(), 2)

    def test_create_tool_employee(self):
        """Сотрудник НЕ может создать инструмент"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'name': 'Болгарка',
            'inventory_number': 'INV-002',
            'category': self.category.id,
            'manufacturer': self.manufacturer.id,
            'status': 'available',
            'location': self.location.id
        }
        response = self.client.post(self.tools_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_tools_by_category(self):
        """Фильтрация инструментов по категории"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.tools_url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_tools_by_status(self):
        """Фильтрация инструментов по статусу"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.tools_url, {'status': 'available'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # ========== TOOL ISSUES ==========

    def test_list_issues_authenticated(self):
        """Авторизованный может смотреть выдачи"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.issues_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_issue_admin(self):
        """Админ может создать выдачу"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'tool': self.tool.id,
            'issued_to': self.employee.id,
            'issued_by': self.admin.id,
            'expected_return_at': '2026-04-01T18:00:00Z'
        }
        response = self.client.post(self.issues_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ToolIssue.objects.count(), 2)

    def test_create_issue_employee(self):
        """Сотрудник НЕ может создать выдачу (только админ/менеджер)"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'tool': self.tool.id,
            'issued_to': self.employee.id,
            'issued_by': self.employee.id,
            'expected_return_at': '2026-04-01T18:00:00Z'
        }
        response = self.client.post(self.issues_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_return_tool(self):
        """Возврат инструмента через отдельный метод (если есть)"""
        pass
