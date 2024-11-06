from flask import Blueprint, request, redirect, url_for, jsonify, flash, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')
 # Импортируем логгер
prompt_bp = Blueprint('prompt', __name__)


# Достать все промпты
@prompt_bp.route('/prompt/get_all', methods=['GET'])
@jwt_required()
def get_prompts():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()
    logger.info(f"Загрузка страницы управления промптами для пользователя: {current_user}", extra={'user_id': current_user['login']})
    prompts = prompt_manager.get_prompts_by_user(current_user['user_id'])

    prompt_data = []

    for s in prompts:
        prompt_info = {
            "prompt_name": s[0],
            "text": s[1],
            "prompt_id": s[2],
            "use_automatic": s[3]
        }

        logger.info(f"Загрузка страницы управления промптами для пользователя: {prompt_info}", extra={'user_id': current_user['login']})
        prompt_data.append(prompt_info)

    return jsonify(prompt_data=prompt_data), 200

# Добавление нового промпта
@prompt_bp.route('/prompt/add', methods=['POST'])
@jwt_required()
def add_prompt():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()
    data = request.json
    prompt_name = data['prompt_name']
    text = data['text']
    try:
        logger.info(f"Добавление нового промпта для пользователя {current_user}: Название: {prompt_name}", extra={'user_id': current_user['login']})
        prompt_id = prompt_manager.add_prompt(current_user['user_id'], prompt_name, text)
        flash('Prompt added successfully', 'success')
    except Exception as e:
        logger.error(f"Ошибка при добавлении промпта: {e}", extra={'user_id': current_user['login']})
        flash('An error occurred while adding the prompt', 'danger')
    return jsonify({"message": "Prompt added successfully", "prompt_id": prompt_id}), 200 



# Удаление промпта
@prompt_bp.route('/prompt/<prompt_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_prompt(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()
    try:
        logger.info(f"Удаление промпта {prompt_id} для пользователя {current_user}", extra={'user_id': current_user['login']})
        prompt_manager.delete_prompt(prompt_id)
        logger.info(f"Промпт {prompt_id} удален для пользователя {current_user}", extra={'user_id': current_user['login']})
        return jsonify(success=True, message='Prompt deleted successfully'), 200
    except Exception as e:
        logger.error(f"Ошибка при удалении промпта: {e}", extra={'user_id': current_user['login']})
        return jsonify(success=False, message='An error occurred while deleting the prompt'), 500



# Редактирование существующего промпта
@prompt_bp.route('/prompt/<prompt_id>/edit', methods=['PATCH'])
@jwt_required()
def edit_prompt(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()

    data = request.get_json()
    new_text = data.get('text')
    new_prompt_name = data.get('prompt_name')  # Получаем новое имя промпта

    try:
        logger.info(f"Изменение промпта {prompt_id} для пользователя {current_user}", extra={'user_id': current_user['login']})
        success = prompt_manager.edit_prompt(prompt_id, new_text, new_prompt_name)  # Передаем новое имя

        if success:
            logger.info(f"Промпт {prompt_id} изменен для пользователя {current_user}", extra={'user_id': current_user['login']})
            return jsonify(success=True, message='Prompt updated successfully'), 200
        else:
            logger.error(f"Промпт {prompt_id} не найден или произошла ошибка", extra={'user_id': current_user['login']})
            return jsonify(success=False, message='Prompt ID not found'), 400

    except Exception as e:
        logger.error(f"Ошибка при изменении промпта: {e}")
        return jsonify(success=False, message=str(e)), 500


@prompt_bp.route('/prompt/<prompt_id>/set_automatic', methods=['PATCH'])
@jwt_required()
def set_automatic(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()

    data = request.get_json()
    use_automatic = data.get('use_automatic')
    logger.info(f"Запрос на изменение флага 'use_automatic' для промпта {prompt_id} пользователем {current_user}: {use_automatic}", extra={'user_id': current_user['login']})
    try:
        # Сначала сбрасываем флаг для всех остальных промптов, если устанавливаем новый флаг
        if use_automatic:
            logger.info(f"Сброс флага 'use_automatic' для всех промптов пользователя {current_user}.", extra={'user_id': current_user['login']})
            prompt_manager.reset_automatic_flag(current_user['user_id'])  # Функция для сброса флага
        # Обновляем выбранный промпт
        prompt_manager.set_automatic_flag(prompt_id, use_automatic)

        logger.info(f"Флаг 'use_automatic' для промпта {prompt_id} успешно обновлён на {use_automatic}.", extra={'user_id': current_user['login']})
        return jsonify(success=True, message='Automatic flag updated successfully'), 200
    except Exception as e:
        logger.error(f"Ошибка при изменении флага: {e}", extra={'user_id': current_user['login']})
        return jsonify(success=False, message=str(e)), 500


# Страница просмотра промпта
@prompt_bp.route('/prompt/<prompt_id>/view', methods=['GET'])
def view_prompt(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    
    prompt = prompt_manager.get_prompt_by_prompt_id(prompt_id)
    
    if prompt:
        return jsonify(prompt)
    else:
        flash('Prompt not found', 'danger')
        return redirect(url_for('prompt.manage_prompts'))
