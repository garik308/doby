# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    cron \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip и устанавливаем Poetry через pip
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry

# Настраиваем Poetry: не создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей без dev
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Копируем весь проект
COPY . .

# Команда по умолчанию (collectstatic теперь запускается через docker-compose command)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "doby.asgi:application"]
