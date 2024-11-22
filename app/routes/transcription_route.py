from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.forms import AudioForm
import logging
from app.utils.db_get import get_audio_name
import json


# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


transcription_bp = Blueprint('transcription', __name__)

@transcription_bp.route('/transcription', methods=['GET'])
def transcription():
    form = AudioForm()
    return render_template('transcription/transcription.html', form=form)

@transcription_bp.route('/transcription_result', methods=['GET'])
def transcription_result():
    return render_template('transcription/transcription_result.html')


@transcription_bp.route('/transcription/create', methods=['POST'])
@jwt_required()
def create_transcription():
    from app.app_celery.tasks.transcription_tasks import process_and_transcribe_audio_task
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    audio_ids = request.json.get('audio_ids')  # Получаем список audio_id
    logger.info(f"Запрос транскрибации аудио с ID {audio_ids}", extra={'user_id': current_user['login']})

    # Проверка на отсутствие audio_id
    if not audio_ids or not isinstance(audio_ids, list):
        logger.warning("Отсутствуют audio_id.", extra={'user_id': current_user['login']})
        return jsonify({'msg': 'Missing audio IDs.'}), 400

    # Запуск задач Celery
    results = []
    for audio_id in audio_ids:
        logger.info(f"Обработка аудио с ID {audio_id} для пользователя {current_user['login']}", extra={'user_id': current_user['login']})
        #str(audio_id), str(current_user['user_id']), str(current_user['login'])
        # Запускаем задачу в Celery
        task = process_and_transcribe_audio_task.delay()

        # Добавляем task_id в список результатов
        results.append({"audio_id": audio_id, "task_id": task.id})

    # Возвращаем список с task_id для отслеживания статуса
    return jsonify({"tasks": results}), 200




@transcription_bp.route('/transcription/all', methods=['GET'])
@jwt_required()
def get_transcriptions():
    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=10, type=int)
    logger.info(f"Запрос транскрипций для пользователя: {current_user} с offset={offset} и limit={limit}", extra={'user_id': current_user['login']})
    
    transcriptions = db.get_transcription_by_user(current_user['user_id'], offset, limit)
    transcription_data = []
    
    for transcription in transcriptions:
        audio_file_name = get_audio_name(transcription['audio_id'])
        transcription_data.append({
            "transcription_id": transcription['transcription_id'],
            "text": transcription['text'],
            "audio_file_name": audio_file_name
        })

    if transcription_data:
        logger.info("Транскрипции найдены.", extra={'user_id': current_user['login']})
        return jsonify(transcription_data), 200
    else:
        logger.warning("Транскрипции не найдены.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "No transcriptions found"}), 404







@transcription_bp.route('/transcription/<transcription_id>/view', methods=['GET'])
@jwt_required()
def get_transcription_view(transcription_id):
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    logger.info(f"Запрос на отображение транскрипции с transcription_id: {transcription_id} для пользователя: {current_user}", extra={'user_id': current_user})
    
    # Передаем только transcription_id в шаблон
    return render_template('transcription/transcription_details.html', transcription_id=transcription_id)





@transcription_bp.route('/user_audio_files', methods=['GET'])
@jwt_required()
def get_user_audio_files():
    from app.database.managers.audio_manager import AudioFileManager
    audio_manager = AudioFileManager()
    current_user = get_jwt_identity()
    current_user=json.loads(current_user)
    logger.info(f"Запрос аудиофайлов для пользователя: {current_user}", extra={'user_id': current_user['login']})
    audio_files = audio_manager.get_audio_files_by_user_for_transcription(current_user['user_id'])

    if audio_files:
        logger.info("Аудиофайлы найдены.", extra={'user_id': current_user['login']})
        #logger.info(f"Найденные аудиофайлы: {audio_files}", extra={'user_id': current_user['login']})
        return jsonify({"audio_files": audio_files}), 200
    else:
        logger.warning("Аудиофайлы не найдены.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "No audio files found"}), 404






