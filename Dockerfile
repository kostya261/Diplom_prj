# Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем системные зависимости (для PostgreSQL, WeasyPrint и сети)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . /app

RUN mkdir -p /app/static /app/media

# Команда для запуска (ждём базу, мигрируем, стартуем)
CMD ["sh", "-c", "while ! nc -z db 5432; do echo 'Ожидаем базу данных...'; sleep 1; done; python manage.py migrate; python manage.py runserver 0.0.0.0:8000"]