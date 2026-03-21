from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersWebTests(TestCase):
    """Тесты для веб-интерфейса users"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            password='test123',
            email='test@test.com',
            phone='+71111111111',
            role='admin'
        )
        self.client.login(username='test', password='test123')

    def test_employee_list_page(self):
        """Список сотрудников открывается"""
        response = self.client.get('/employees/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test')

    def test_employee_add_page(self):
        """Страница добавления сотрудника открывается"""
        response = self.client.get('/employees/add/')
        self.assertEqual(response.status_code, 200)

    def test_employee_edit_page(self):
        """Страница редактирования сотрудника открывается"""
        response = self.client.get(f'/employees/{self.user.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test')

    def test_profile_page(self):
        """Страница профиля открывается"""
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test')

    def test_profile_edit_page(self):
        """Страница редактирования профиля открывается"""
        response = self.client.get('/profile/edit/')
        self.assertEqual(response.status_code, 200)
