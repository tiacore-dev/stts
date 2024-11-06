from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

account_bp = Blueprint('account', __name__)



@account_bp.route('/get_username', methods=['GET'])
@jwt_required()  # Требуется авторизация с JWT
def get_username():
    current_user = get_jwt_identity()
    from app.database.managers.user_manager import UserManager
    # Создаем экземпляр менеджера базы данных
    db = UserManager()
    logger.info(f"Запрос имени пользователя от пользователя: {current_user['user_id']}", extra={'user_id': current_user['login']})
    user=db.get_user_by_user_id(current_user['user_id'])
    username=user.username
    logger.info(f"Получено имя пользователя: {username}", extra={'user_id': current_user['login']})
    return jsonify(username), 200


@account_bp.route('/set_api_token', methods=['POST'])
@jwt_required() 
def set_api_token():
    data = request.json
    comment=data.get('comment')
    current_user = get_jwt_identity()
    from app.database.managers.api_keys_manager import APIKeysManager
    db = APIKeysManager()
    logger.info(f"Запрос о создании API ключа от пользователя: {current_user}", extra={'user_id': current_user['login']})
    
    if db.add_api_key(current_user['user_id'], comment):
        return jsonify({"message": "API key created successfully"}), 200
    else:
        return jsonify({"error": "Database error"}), 500

@account_bp.route('/refresh_api_token', methods=['PATCH'])
@jwt_required()  # Требуется авторизация с JWT
def refresh_api_token():
    data = request.json
    comment=data.get('comment')
    current_user = get_jwt_identity()
    from app.database.managers.api_keys_manager import APIKeysManager
    db = APIKeysManager()
    logger.info(f"Запрос о новом API ключе от пользователя: {current_user}", extra={'user_id': current_user['login']})
    
    if db.refresh_api_key(current_user['user_id'], comment):
        return jsonify({"message": "API key updated successfully"}), 200
    else:
        return jsonify({"error": "Database error"}), 500
