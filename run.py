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
from flask_jwt_extended import exceptions
from flask import jsonify, request

@app.before_request
def log_request_info():
    logger.debug(f"Headers: {request.headers}")

@app.errorhandler(exceptions.JWTDecodeError)
def handle_jwt_decode_error(e):
    logger.error(f"Ошибка декодирования JWT: {str(e)}")
    return jsonify({"error": "Invalid token"}), 422

@app.errorhandler(422)
def handle_unprocessable_entity(e):
    logger.error(f"422 Error: {str(e)}")
    return jsonify({"error": "Invalid input"}), 422

# Запуск через Gunicorn будет автоматически управлять процессом запуска
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
