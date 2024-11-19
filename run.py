from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем порт из переменных окружения
port = os.getenv('FLASK_PORT', 5064)

# Создаем приложение
app, socketio = create_app()

# Запуск через Gunicorn будет автоматически управлять процессом запуска
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
