import subprocess
import sys
import os

# Запускаем dumpdata и принудительно устанавливаем UTF-8
result = subprocess.run(
    [sys.executable, 'manage.py', 'dumpdata',
     '--exclude', 'auth.permission',
     '--exclude', 'contenttypes',
     '--exclude', 'admin.logentry',
     '--exclude', 'sessions.session',
     '--indent', '2'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
)

# Сохраняем с явной UTF-8 кодировкой
with open('fixtures/demo_data.json', 'w', encoding='utf-8') as f:
    f.write(result.stdout)

print("✅ Данные сохранены в fixtures/demo_data.json")
print(f"Размер файла: {len(result.stdout)} байт")
