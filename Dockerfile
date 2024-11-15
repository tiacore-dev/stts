# Используем официальный образ Python в качестве базового
FROM python:3.9-slim

# Устанавливаем необходимые зависимости, включая ffmpeg, curl, gcc, libpq-dev и библиотеки для SSL
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    gcc \
    libpq-dev \
    ca-certificates \            # Устанавливаем сертификаты для SSL
    libssl-dev \                 # Устанавливаем OpenSSL для работы с SSL/TLS
    && rm -rf /var/lib/apt/lists/*

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в рабочую директорию
COPY requirements.txt .

# Обновляем pip до последней версии
RUN python -m pip install --upgrade pip

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения в рабочую директорию
COPY . .

# Указываем команду для запуска приложения
CMD ["python", "run.py"]
