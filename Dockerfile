# Используем официальный образ Python в качестве базового
FROM python:3.9-slim

# Устанавливаем необходимые зависимости, включая ffmpeg, curl, gcc и библиотеки для SSL
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    gcc \
    libpq-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && update-ca-certificates


# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в рабочую директорию
COPY requirements.txt .

# Обновляем pip до последней версии
RUN python -m pip install --upgrade pip

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Gunicorn
RUN pip install gunicorn

# Копируем сертификаты в контейнер (предполагается, что они находятся в папке certs на хосте)
COPY ./certs /app/certs

# Указываем контейнеру путь к сертификатам
#ENV SSL_CERT_FILE=/app/certs/fullchain.pem
#ENV SSL_KEY_FILE=/app/certs/privkey.pem

# Копируем весь код приложения в рабочую директорию
COPY . .

# Указываем команду для запуска приложения
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${FLASK_PORT}", "run:app"]
