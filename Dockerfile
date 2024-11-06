# Используем официальный образ Python в качестве базового
FROM python:3.9-slim



# Копируем wait-for-it.sh в контейнер
# Устанавливаем необходимые зависимости (curl, чтобы скачать wait-for-it)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && curl -o /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /wait-for-it.sh

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
