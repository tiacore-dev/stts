from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import json
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

account_bp = Blueprint('account', __name__)

@account_bp.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

@account_bp.route('/api-keys', methods=['GET'])
def api_key():
    return render_template('api_keys.html')

@account_bp.route('/account', methods=['GET'])
def account():
    return render_template('account.html')

@account_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user = get_jwt_identity()
        current_user=json.loads(current_user)
        logger.info(f"Пользователь авторизован: {current_user}")
        return jsonify({"message": "Access granted"}), 200
    except Exception as e:
        logger.error(f"Ошибка авторизации: {str(e)}")
        return jsonify({"error": "Authorization failed"}), 401


@account_bp.route('/get_username', methods=['GET'])
@jwt_required()  # Требуется авторизация с JWT
def get_username():
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    from app.database.managers.user_manager import UserManager
    # Создаем экземпляр менеджера базы данных
    db = UserManager()
    logger.info(f"Запрос имени пользователя от пользователя: {current_user['user_id']}", extra={'user_id': current_user['login']})
    user=db.get_user_by_user_id(current_user['user_id'])
    username=user.username
    logger.info(f"Получено имя пользователя: {username}", extra={'user_id': current_user['login']})
    return jsonify(username), 200


@account_bp.route('/api-key/create', methods=['POST'])
@jwt_required() 
def set_api_token():
    data = request.json
    comment = data.get('comment')
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    from app.database.managers.api_keys_manager import APIKeysManager
    db = APIKeysManager()
    logger.info(f"Запрос о создании API ключа от пользователя: {current_user}", extra={'user_id': current_user['login']})
    
    api_key = db.add_api_key(current_user['user_id'], comment)
    if api_key:
        return jsonify({"message": "API key created successfully", "api_key": api_key}), 200  # Возвращаем ключ
    else:
        return jsonify({"error": "Database error"}), 500

@account_bp.route('/api-key/delete', methods=['DELETE'])
@jwt_required()  # Требуется авторизация с JWT
def delete_api_token():
    data = request.json
    key_id = data.get('key_id')
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    from app.database.managers.api_keys_manager import APIKeysManager
    db = APIKeysManager()
    logger.info(f"Запрос об удалении API ключа от пользователя: {current_user}", extra={'user_id': current_user['login']})
    
    api_key = db.delete_api_key(key_id)
    if api_key:
        return jsonify({"message": "API key deleted successfully"}), 200  # Возвращаем ключ
    else:
        return jsonify({"error": "Database error"})

@account_bp.route('/api-key/all', methods=['GET'])
@jwt_required()
def get_api_tokens():
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    from app.database.managers.api_keys_manager import APIKeysManager
    db = APIKeysManager()
    logger.info(f"Запрос всех API ключей от пользователя: {current_user}", extra={'user_id': current_user['login']})
    api_keys=db.get_api_keys(current_user['user_id'])
    logger.info(f"{api_keys}", extra={'user_id': current_user['login']})
    return jsonify(api_keys), 200