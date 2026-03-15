from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Task
from datetime import date, timedelta

User = get_user_model()


class TasksWebTests(TestCase):
    """Тесты для веб-интерфейса tasks"""

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
        self.employee = User.objects.create_user(
            username='employee',
            password='test123',
            email='emp@test.com',
            phone='+72222222222',
            role='employee'
        )

        self.task = Task.objects.create(
            title='Тестовая задача',
            responsible=self.employee,
            deadline=date.today() + timedelta(days=7),
            created_by=self.user
        )

    def test_task_list_page(self):
        """Список задач открывается"""
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')

    def test_task_add_page(self):
        """Страница создания задачи открывается"""
        response = self.client.get('/tasks/add/')
        self.assertEqual(response.status_code, 200)

    def test_task_edit_page(self):
        """Страница редактирования задачи открывается"""
        response = self.client.get(f'/tasks/{self.task.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')
