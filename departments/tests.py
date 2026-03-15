
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Department

User = get_user_model()


class DepartmentTests(APITestCase):
    """Тесты для отделов"""

    def setUp(self):
        """Создаём тестовых пользователей"""
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

        # Тестовый отдел
        self.department = Department.objects.create(
            name='IT-отдел',
            code='IT',
            is_active=True
        )

        # URL для списка отделов
        self.list_url = reverse('department-list')  # имя из роутера

    def test_list_departments_authenticated(self):
        """Авторизованный пользователь может видеть список отделов"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_departments_unauthenticated(self):
        """Неавторизованный пользователь не может видеть отделы"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_department_admin(self):
        """Админ может создать отдел"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Бухгалтерия',
            'code': 'ACC',
            'is_active': True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

    def test_create_department_manager(self):
        """Менеджер может создать отдел (IsAdminOrManager)"""
        self.client.force_authenticate(user=self.manager)
        data = {
            'name': 'Бухгалтерия',
            'code': 'ACC',
            'is_active': True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

    def test_create_department_employee(self):
        """Сотрудник НЕ может создать отдел"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'name': 'Бухгалтерия',
            'code': 'ACC',
            'is_active': True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Department.objects.count(), 1)

    def test_retrieve_department(self):
        """Получение конкретного отдела"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('department-detail', args=[self.department.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'IT-отдел')

    def test_update_department_admin(self):
        """Админ может обновить отдел"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('department-detail', args=[self.department.id])
        data = {'name': 'ИТ-департамент'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.department.refresh_from_db()
        self.assertEqual(self.department.name, 'ИТ-департамент')

    def test_update_department_employee(self):
        """Сотрудник НЕ может обновить отдел"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('department-detail', args=[self.department.id])
        data = {'name': 'ИТ-департамент'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.department.refresh_from_db()
        self.assertEqual(self.department.name, 'IT-отдел')

    def test_delete_department_admin(self):
        """Админ может удалить отдел"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('department-detail', args=[self.department.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Department.objects.count(), 0)

    def test_delete_department_employee(self):
        """Сотрудник НЕ может удалить отдел"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('department-detail', args=[self.department.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Department.objects.count(), 1)

    def test_search_departments(self):
        """Поиск по названию отдела"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.list_url, {'search': 'IT'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(self.list_url, {'search': 'бухгалтерия'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
