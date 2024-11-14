from functools import wraps
from flask import jsonify, request


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Извлекаем API ключ из заголовка
        api_key = request.headers.get('API-Key')
        
        if not api_key:
            return jsonify({"error": "API key is missing"}), 400
        from app.database.managers.api_keys_manager import APIKeysManager
        # Проверяем существование API ключа в базе данных
        db = APIKeysManager()
        user_id = db.get_user_by_api_key(api_key)

        if not user_id:
            return jsonify({"error": "Invalid API key"}), 403

        # Добавляем информацию о пользователе в запрос (например, для доступа к данным пользователя)
        request.user_id = user_id

        return f(*args, **kwargs)
    
    return decorated_function