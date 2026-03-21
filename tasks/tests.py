from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import Task, TaskComment, TaskStatusLog

User = get_user_model()


class TaskTests(APITestCase):
    """Тесты для задач"""

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

        # Ещё один сотрудник
        self.employee2 = User.objects.create_user(
            username='employee2',
            password='employee1234',
            email='employee2@test.com',
            phone='+74444444444',
            role='employee',
            first_name='Second',
            last_name='Employee'
        )

        # Тестовая задача
        self.task = Task.objects.create(
            title='Тестовая задача',
            description='Описание тестовой задачи',
            responsible=self.employee,
            created_by=self.manager,
            deadline=date.today() + timedelta(days=7),
            priority=Task.Priority.MEDIUM,
            status=Task.Status.NEW
        )
        self.task.co_executors.add(self.employee2)

        # Тестовый комментарий
        self.comment = TaskComment.objects.create(
            task=self.task,
            author=self.employee,
            text='Тестовый комментарий'
        )

        # URL-ы
        self.tasks_url = reverse('task-list')
        # Для вложенных ViewSet'ов используем имена с префиксом
        self.comments_url = '/api/tasks/comments/'
        self.logs_url = '/api/tasks/logs/'
        self.task_detail_url = reverse('task-detail', args=[self.task.id])
        self.change_status_url = f'/api/tasks/{self.task.id}/change_status/'
        self.add_comment_url = f'/api/tasks/{self.task.id}/add_comment/'
        self.employee_load_url = '/api/tasks/employee_load/'
        self.important_tasks_url = '/api/tasks/important_tasks/'

    # ========== BASIC CRUD ==========

    def test_list_tasks_authenticated(self):
        """Авторизованный может видеть список задач"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_tasks_unauthenticated(self):
        """Неавторизованный не может видеть задачи"""
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_sees_only_own_tasks(self):
        """Сотрудник видит только свои задачи"""
        # Создаём задачу для другого сотрудника
        Task.objects.create(
            title='Чужая задача',
            responsible=self.employee2,
            created_by=self.manager,
            deadline=date.today() + timedelta(days=7)
        )

        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # только своя задача
        self.assertEqual(response.data['results'][0]['title'], 'Тестовая задача')

    def test_manager_sees_all_tasks(self):
        """Менеджер видит все задачи"""
        # Создаём задачу для другого сотрудника
        Task.objects.create(
            title='Чужая задача',
            responsible=self.employee2,
            created_by=self.manager,
            deadline=date.today() + timedelta(days=7)
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_task_admin(self):
        """Админ может создать задачу"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'title': 'Новая задача',
            'responsible': self.employee.id,
            'deadline': (date.today() + timedelta(days=14)).isoformat(),
            'priority': 'high'
        }
        response = self.client.post(self.tasks_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_create_task_manager(self):
        """Менеджер может создать задачу"""
        self.client.force_authenticate(user=self.manager)
        data = {
            'title': 'Новая задача',
            'responsible': self.employee.id,
            'deadline': (date.today() + timedelta(days=14)).isoformat(),
            'priority': 'high'
        }
        response = self.client.post(self.tasks_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_create_task_employee(self):
        """Сотрудник НЕ может создать задачу"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'title': 'Новая задача',
            'responsible': self.employee.id,
            'deadline': (date.today() + timedelta(days=14)).isoformat()
        }
        response = self.client.post(self.tasks_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Task.objects.count(), 1)

    def test_update_task_admin(self):
        """Админ может обновить задачу"""
        self.client.force_authenticate(user=self.admin)
        url = self.task_detail_url
        data = {'title': 'Обновлённая задача'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Обновлённая задача')

    def test_update_task_employee_not_allowed(self):
        """Сотрудник НЕ может обновить задачу (кроме статуса)"""
        self.client.force_authenticate(user=self.employee)
        url = self.task_detail_url
        data = {'title': 'Попытка взлома'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========== CHANGE STATUS ==========

    def test_change_status_employee_own_task(self):
        """Сотрудник может менять статус своей задачи"""
        self.client.force_authenticate(user=self.employee)
        data = {'status': 'in_progress', 'comment': 'Приступаю'}
        response = self.client.post(self.change_status_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')
        self.assertIsNotNone(self.task.started_at)

        # Проверяем, что создался лог
        self.assertTrue(TaskStatusLog.objects.filter(task=self.task).exists())

    def test_change_status_employee_not_own_task(self):
        """Сотрудник НЕ может менять статус чужой задачи (даже не видит её)"""
        other_task = Task.objects.create(
            title='Чужая задача',
            responsible=self.employee2,
            created_by=self.manager,
            deadline=date.today() + timedelta(days=7)
        )

        self.client.force_authenticate(user=self.employee)
        url = f'/api/tasks/{other_task.id}/change_status/'
        data = {'status': 'in_progress'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_change_status_manager_any_task(self):
        """Менеджер может менять статус любой задачи"""
        self.client.force_authenticate(user=self.manager)
        data = {'status': 'in_progress'}
        response = self.client.post(self.change_status_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ========== COMMENTS ==========

    def test_add_comment_employee_own_task(self):
        """Сотрудник может комментировать свою задачу"""
        self.client.force_authenticate(user=self.employee)
        data = {'text': 'Новый комментарий'}
        response = self.client.post(self.add_comment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskComment.objects.count(), 2)
        self.assertEqual(TaskComment.objects.last().text, 'Новый комментарий')

    def test_add_comment_employee_not_own_task(self):
        """Сотрудник НЕ может комментировать чужую задачу (даже не видит её)"""
        other_task = Task.objects.create(
            title='Чужая задача',
            responsible=self.employee2,
            created_by=self.manager,
            deadline=date.today() + timedelta(days=7)
        )

        self.client.force_authenticate(user=self.employee)
        url = f'/api/tasks/{other_task.id}/add_comment/'
        data = {'text': 'Комментарий к чужой задаче'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ========== SPECIAL ENDPOINTS ==========

    def test_employee_load_endpoint_admin(self):
        """Спецэндпоинт загруженности доступен админу"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.employee_load_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_employee_load_endpoint_employee(self):
        """Спецэндпоинт загруженности НЕ доступен сотруднику"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.employee_load_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_important_tasks_endpoint_admin(self):
        """Спецэндпоинт важных задач доступен админу"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.important_tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_important_tasks_endpoint_employee(self):
        """Спецэндпоинт важных задач НЕ доступен сотруднику"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.important_tasks_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========== COMMENTS VIEWSET ==========

    def test_list_comments_authenticated(self):
        """Авторизованный может видеть комментарии"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 1)

    def test_create_comment_employee(self):
        """Сотрудник может создать комментарий (через отдельный эндпоинт)"""
        self.client.force_authenticate(user=self.employee)
        data = {'text': 'Комментарий через тест'}
        response = self.client.post(self.add_comment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ========== STATUS LOGS ==========

    def test_logs_endpoint_admin(self):
        """Логи статусов доступны админу"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logs_endpoint_employee(self):
        """Логи статусов НЕ доступны сотруднику"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
