from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает демонстрационные данные'

    def handle(self, *args, **options):
        # Очищаем существующие данные (кроме суперпользователя)
        self.stdout.write('Очищаем базу...')

        # Удаляем всё, кроме суперпользователей
        with connection.cursor() as cursor:
            cursor.execute("""
                TRUNCATE TABLE
                    tasks_taskcomment,
                    tasks_taskstatuslog,
                    tasks_task,
                    inventory_toolissue,
                    inventory_tool,
                    inventory_storagelocation,
                    inventory_toolmanufacturer,
                    inventory_toolcategory,
                    warehouse_stockmovement,
                    warehouse_product,
                    warehouse_productmanufacturer,
                    warehouse_productcategory,
                    departments_department
                RESTART IDENTITY CASCADE;
            """)

        # Загружаем демо-данные
        self.stdout.write('Загружаем демо-данные...')
        call_command('loaddata', 'demo_data.json')

        # Создаём тестового пользователя, если его нет
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user(
                username='demo',
                password='demo123',
                email='demo@example.com',
                phone='+79999999999',
                role='employee',
                first_name='Демо',
                last_name='Пользователь'
            )
            self.stdout.write(self.style.SUCCESS('Создан демо-пользователь (логин: demo, пароль: demo123)'))

        self.stdout.write(self.style.SUCCESS('База успешно загружена!'))
