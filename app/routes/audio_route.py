from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Response, jsonify, render_template
import logging
import tempfile
from app.utils.upload_audio import process_and_upload_file
import json
from app.app_celery.tasks.audio_tasks import process_and_upload_file_task

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

audio_bp = Blueprint('audio', __name__)

# Отображение страницы загрузки аудиофайлов
@audio_bp.route('/manage_audio', methods=['GET'])
def manage_audio():
    return render_template('manage_audio.html')


@audio_bp.route('/audio/upload', methods=['POST'])
@jwt_required()
def upload_audio():
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    user_login = str(current_user['login'])
    logger.info(f"Пользователь {user_login} прислал файлы для загрузки.", extra={'user_id': user_login})

    # Получаем файлы и их имена
    files = request.files.getlist('files')
    file_names = request.form.getlist('fileNames')
    
    if not files or not file_names:
        logger.error(f"Пользователь {user_login} не выбрал файлы для загрузки.", extra={'user_id': user_login})
        return jsonify({'error': 'No files provided'}), 400

    result = []
    logger.info(f"Начата обработка файлов.", extra={'user_id': user_login})

    current_app.extensions['socketio'].emit('upload_progress', {'message': 'Загрузка началась', 'status': 'started'}, room=user_login)

    # Цикл по файлам и именам
    for file, file_name_input in zip(files, file_names):
        # Передаем сам файл в функцию обработки
        #file, current_user['user_id'], file_name_input, user_login
        #'file_path', current_user['user_id'], file_name_input, user_login
        task = process_and_upload_file_task.apply_async()
        #audio_id = upload_result.get('audio_id')
#upload_result
        result.append({"file_name": file_name_input, "task_id": task.id})

    return jsonify(result), 200



#temp_file_path, current_user['user_id'], file_name_input, user_login


# Получение списка файлов с пагинацией
@audio_bp.route('/audio/all', methods=['GET'])
@jwt_required()
def get_files():
    from app.database.managers.audio_manager import AudioFileManager
    
    db = AudioFileManager()
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    logger.info(f"Пользователь {current_user} запрашивает список файлов.", extra={'user_id': current_user['login']})

    page = int(request.args.get('page', 1))
    per_page = 10

    try:
        logger.info(f"{current_user['user_id']}", extra={'user_id': current_user['login']})
        # Получаем файлы для текущего пользователя
        files = db.get_audio_files_by_user(current_user['user_id'])
        if files is None:
            logger.warning("Не удалось получить файлы пользователя.", extra={'user_id': current_user['login']})
            return jsonify({'error': 'No files found'}), 404
        total_files = len(files)
        total_pages = (total_files + per_page - 1) // per_page
        
        # Пагинация
        files_paginated = files[(page - 1) * per_page: page * per_page]
        
        file_data = [
            {
                'audio_id': f[0],
                'name': f[1],  # file_name
                's3_key': f[2],  # s3_key
                'bucket_name': f[3],  # bucket_name
                'transcribed': f[4] #транскрибировано ли аудио
            }
            for f in files_paginated
        ]

        logger.info(f"Отправлен список файлов для страницы {page}.", extra={'user_id': current_user['login']})
        return jsonify({'files': file_data, 'total_pages': total_pages}), 200
    except Exception as e:
        logger.error(f"Ошибка при получении списка файлов: {e}", extra={'user_id': current_user['login']})
        return jsonify({'error': 'Failed to retrieve files'}), 500



# Удаление файла
@audio_bp.route('/audio/<audio_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_file(audio_id):
    from app.database.managers.audio_manager import AudioFileManager
    db = AudioFileManager()
    from app.services.s3 import get_s3_manager, get_bucket_name
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)

    if not audio_id:
        return jsonify({'error': 'No file name provided'}), 400

    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()

    # Проверяем, что файл принадлежит текущему пользователю
    file_record = db.get_audio_file_by_id(current_user['user_id'], audio_id)
    if not file_record:
        return jsonify({'error': 'File not found or access denied'}), 404

    try:
        # Удаляем файл из S3
        s3_manager.delete_file(bucket_name,file_record.s3_key)
        audio_id=file_record.audio_id
        db.delete_audio_file(audio_id)  # Метод для удаления записи из базы
        logger.info(f"Файл {audio_id} успешно удален.", extra={'user_id': current_user['login']})
        return jsonify({'message': 'File deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Ошибка при удалении файла: {e}", extra={'user_id': current_user['login']})
        return jsonify({'error': 'File deletion failed'}), 500


@audio_bp.route('/audio/<audio_id>/download', methods=['GET'])
@jwt_required()
def download_file_bytes():
    from app.database.managers.audio_manager import AudioFileManager
    db = AudioFileManager()
    from app.services.s3 import get_s3_manager, get_bucket_name
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    audio_id = request.args.get('audio_id')

    logger.info(f"Получен запрос на скачивание файла: {audio_id} для пользователя: {current_user}", extra={'user_id': current_user['login']})

    if not audio_id:
        logger.warning("Имя файла не указано.", extra={'user_id': current_user['login']})
        return jsonify({'error': 'No file name provided'}), 400

    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()

    # Проверяем, что файл принадлежит текущему пользователю
    file_record = db.get_audio_file_by_id(current_user['user_id'], audio_id)
    if not file_record:
        logger.warning(f"Файл '{audio_id}' не найден или доступ запрещен для пользователя '{current_user}'.", extra={'user_id': current_user['login']})
        return jsonify({'error': 'File not found or access denied'}), 404

    try:
        # Получаем файл из S3
        audio_bytes = s3_manager.get_file(bucket_name, file_record.s3_key)
        if audio_bytes is None:
            logger.error(f"Не удалось получить содержимое файла '{audio_id}' из S3.", extra={'user_id': current_user['login']})
            return jsonify({'error': 'Could not retrieve audio file'}), 500
        
        return Response(audio_bytes, mimetype='audio/mpeg')  # Укажите корректный тип контента
    except Exception as e:
        logger.error(f"Ошибка при получении аудиофайла '{audio_id}' из S3: {str(e)}", extra={'user_id': current_user['login']})
        return jsonify({'error': f'Could not retrieve audio file: {str(e)}'}), 500


@audio_bp.route('/audio/<audio_id>/download_url', methods=['GET'])
@jwt_required()
def download_file(audio_id):
    from app.database.managers.audio_manager import AudioFileManager
    db = AudioFileManager()
    from app.services.s3 import get_s3_manager, get_bucket_name
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    #audio_id = request.args.get('audio_id')

    if not audio_id:
        return jsonify({'error': 'No file name provided'}), 400

    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()

    file_record = db.get_audio_file_by_id(current_user['user_id'], audio_id)
    if not file_record:
        return jsonify({'error': 'File not found or access denied'}), 404

    # Генерируем временный URL для скачивания файла
    url = s3_manager.generate_presigned_url(bucket_name, file_record.s3_key)

    if url:
        return jsonify({'url': url}), 200
    else:
        return jsonify({'error': 'Could not generate download URL'}), 500


