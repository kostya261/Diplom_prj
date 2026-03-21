from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from departments.models import Department

User = get_user_model()


class UserTests(APITestCase):
    """Тесты для пользователей"""

    def setUp(self):
        """Создаём тестовых пользователей и объекты"""
        self.department = Department.objects.create(
            name='IT-отдел',
            code='IT',
            is_active=True
        )

        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            phone='+71111111111',
            role='admin',
            first_name='Admin',
            last_name='Adminov'
        )

        self.manager = User.objects.create_user(
            username='manager',
            password='manager123',
            email='manager@test.com',
            phone='+72222222222',
            role='manager',
            first_name='Manager',
            last_name='Managerov'
        )

        self.employee = User.objects.create_user(
            username='employee',
            password='employee123',
            email='employee@test.com',
            phone='+73333333333',
            role='employee',
            first_name='Employee',
            last_name='Employeov',
            department=self.department
        )

        self.users_url = reverse('user-list')

    # ========== LIST ==========

    def test_list_users_admin(self):
        """Админ видит всех пользователей"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_list_users_manager(self):
        """Менеджер видит всех пользователей"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_list_users_employee(self):
        """Сотрудник видит только себя"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'employee')

    def test_list_users_unauthenticated(self):
        """Неавторизованный пользователь не может видеть список"""
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========== RETRIEVE ==========

    def test_retrieve_user_admin(self):
        """Админ может просматривать любого пользователя"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-detail', args=[self.employee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'employee')

    def test_retrieve_user_employee_self(self):
        """Сотрудник может просматривать себя"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('user-detail', args=[self.employee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'employee')

    def test_retrieve_user_employee_other(self):
        """Сотрудник НЕ может просматривать другого пользователя"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('user-detail', args=[self.manager.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ========== CREATE ==========

    def test_create_user_admin(self):
        """Админ может создать пользователя"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@test.com',
            'phone': '+79999999999',
            'role': 'employee',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.users_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)

    def test_create_user_manager(self):
        """Менеджер НЕ может создать пользователя"""
        self.client.force_authenticate(user=self.manager)
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@test.com',
            'phone': '+79999999999',
            'role': 'employee'
        }
        response = self.client.post(self.users_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_employee(self):
        """Сотрудник НЕ может создать пользователя"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@test.com',
            'phone': '+79999999999',
            'role': 'employee'
        }
        response = self.client.post(self.users_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)

    # ========== UPDATE ==========

    def test_update_user_admin(self):
        """Админ может обновить любого пользователя"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-detail', args=[self.employee.id])
        data = {'first_name': 'Updated'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.first_name, 'Updated')

    def test_update_user_employee_self_not_allowed(self):
        """Сотрудник НЕ может обновить себя (только админ)"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('user-detail', args=[self.employee.id])
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_employee_other(self):
        """Сотрудник НЕ может обновить другого пользователя"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('user-detail', args=[self.manager.id])
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========== DELETE ==========

    def test_delete_user_admin(self):
        """Админ может удалить пользователя"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-detail', args=[self.employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 2)

    def test_delete_user_manager(self):
        """Менеджер НЕ может удалить пользователя"""
        self.client.force_authenticate(user=self.manager)
        url = reverse('user-detail', args=[self.employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)

    # ========== FILTERS ==========

    def test_filter_by_role(self):
        """Фильтрация пользователей по роли"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.users_url, {'role': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'admin')

    def test_filter_by_department(self):
        """Фильтрация пользователей по отделу"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.users_url, {'department': self.department.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'employee')

    # ========== SEARCH ==========

    def test_search_by_username(self):
        """Поиск пользователей по username"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.users_url, {'search': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'admin')

    def test_search_by_email(self):
        """Поиск пользователей по email"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.users_url, {'search': 'employee@test.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'employee')
