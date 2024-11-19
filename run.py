from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем порт из переменных окружения
port = os.getenv('FLASK_PORT', 5064)

# Создаем приложение
#app, socketio = create_app()
app = create_app()

import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


# Запуск через Gunicorn будет автоматически управлять процессом запуска
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
