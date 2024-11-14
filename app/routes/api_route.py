from flask import Blueprint, request, jsonify, current_app
from flask import jsonify
import logging
from app.utils.process_audio_api import process_and_transcribe_audio_1, process_and_transcribe_audio_2
from functools import wraps
import requests
import os
from urllib.parse import urlparse, unquote
from app.utils.db_get import get_prompt, get_transcription
from app.utils.db_get import get_audio_name, get_prompt_name
import uuid
from app.services.openai.analyze_text import analyze_text

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

api_bp = Blueprint('api', __name__)

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

@api_bp.route('/api/transcription/create', methods=['POST'])
@api_key_required
def create_transcription_api():
    from app.database.managers.audio_manager import AudioFileManager

    db = AudioFileManager()
    # Извлекаем данные из запроса
    audio_url = request.json.get('audio_url')
    channels = request.json.get('channels', 1)  # Если channels не передан, по умолчанию один канал
    new_filename = request.json.get('new_filename', None)  # Новое имя файла, если передано
    prompt = request.json.get('prompt', None)

    # Получаем user_id, который был добавлен в декораторе
    user_id = request.user_id
    if not audio_url:
        return jsonify({"error": "Audio URL is required"}), 400
    
    # Получаем аудиофайл по ссылке
    try:
        response = requests.get(audio_url)
        if response.status_code != 200:
            logger.error(f"Ошибка загрузки: {response.status_code} - {response.text}")
            return jsonify({"error": "Failed to download audio file"}), 400
        audio_file = response.content  # Получаем содержимое аудиофайла
        # Получаем размер файла из заголовка Content-Length
        file_size = int(response.headers.get('Content-Length', 0))
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла по URL {audio_url}: {e}")
        return jsonify({"error": "Error downloading audio file"}), 500
    
    # Парсим URL и получаем путь без параметров
    parsed_url = urlparse(audio_url)
    path = parsed_url.path  # Здесь мы имеем только путь к файлу без параметров

    # Декодируем и получаем оригинальное название файла
    original_filename = os.path.basename(unquote(path))  # unquote декодирует URL-кодировку
    # Извлекаем имя файла и расширение
    logger.info(f"Оригинальное название: {original_filename}")
    file_name, file_extension = os.path.splitext(original_filename)
    logger.info(f"Получившиеся название и расширение файла: {file_name}, {file_extension}")
    
    # Если новое имя файла передано, используем его, иначе оставляем оригинальное
    final_filename = new_filename if new_filename else file_name
    logger.info(f'Финальное название: {final_filename}')

    audio_id = db.add_audio_file(user_id, final_filename, file_extension, file_size, url=audio_url)
    logger.info(f"Полученное аудио с ID: {audio_id}")
    # Выбираем функцию для транскрипции в зависимости от количества каналов
    transcription_id = str(uuid.uuid4())
    current_app.extensions['socketio'].emit('transcription_status', {
        'status': 'started', 
        'transcription_id': transcription_id, 
        'user_id': user_id,
        'filename': final_filename
    })
    if channels == 1:
        text = process_and_transcribe_audio_1(audio_file, user_id, audio_id, file_extension, prompt)
    elif channels == 2:
        text = process_and_transcribe_audio_2(audio_file, user_id, audio_id, file_extension, prompt)
    else:
        return jsonify({"error": "Invalid number of channels"}), 400
    

    # Возвращаем ID транскрипции и новое имя файла
    return jsonify({
        'transcription_id': transcription_id, 'transcription_text': text
    })


@api_bp.route('/api/transcription/<transcription_id>', methods=['GET'])
@api_key_required
def get_transcription_by_id(transcription_id):
    # Получаем user_id, который был добавлен в декораторе
    user_id = request.user_id
    logger.info(f"Запрос на получение транскрипции по transcription_id: {transcription_id} для пользователя: {user_id}", extra={'user_id': user_id})
    from app.database.managers.transcription_manager import TranscriptionManager
    
    db = TranscriptionManager()
    transcription = db.get_transcription_by_id(transcription_id)

    if transcription:
        return jsonify({
            'transcription_id': transcription.transcription_id,  # Убедитесь, что это поле существует
            'text': transcription.text,
            'audio_id': transcription.audio_id,
            'tokens': transcription.tokens
        }), 200
    else:
        logger.warning("Транскрипция не найдена.", extra={'user_id': user_id})
        return jsonify({"msg": "Transcription not found"}), 404
    

@api_bp.route('/transcription/all', methods=['GET'])
@api_key_required
def get_transcriptions():
    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()
    user_id = request.user_id
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=0, type=int)
    logger.info(f"Запрос транскрипций для пользователя: {user_id} с offset={offset} и limit={limit}", extra={'user_id': user_id})
    
    transcriptions = db.get_transcription_by_user(user_id, offset, limit)
    transcription_data = []
    
    for transcription in transcriptions:
        audio_file_name = get_audio_name(transcription['audio_id'])
        transcription_data.append({
            "transcription_id": transcription['transcription_id'],
            "text": transcription['text'],
            "audio_file_name": audio_file_name
        })

    if transcription_data:
        logger.info("Транскрипции найдены.", extra={'user_id': user_id})
        return jsonify(transcription_data), 200
    else:
        logger.warning("Транскрипции не найдены.", extra={'user_id': user_id})
        return jsonify({"msg": "No transcriptions found"}), 404


@api_bp.route('/api/analysis/create', methods=['POST'])
@api_key_required
def create_analysis_api():
    from app.database.managers.analysis_manager import AnalysisManager
    db = AnalysisManager()
    data = request.json
    prompt_id = data.get('prompt_id', None)
    custom_prompt=data.get('prompt', None)
    transcription_id = data['transcription_id']  # Получаем  transcription_id
    user_id = request.user_id
    logger.info(f"Запрос анализа транскрибаций с ID {transcription_id} и промптом с ID: {prompt_id}.", extra={'user_id': user_id})
    # Получаем prompt для анализа
    if prompt_id:
        prompt = get_prompt(prompt_id)
    if custom_prompt:
        prompt=custom_prompt
        from app.database.managers.prompt_manager import PromptManager
        db_p=PromptManager()
        prompt_id = db_p.add_prompt(user_id, 'custom_prompt', prompt)
    transcription = get_transcription(transcription_id)  # Получаем транскрипцию
    logger.info(f"Начат анализ транскрибаций.", extra={'user_id': user_id})
    analysis, tokens=analyze_text(prompt, transcription)  # Добавляем задачу анализа текста
    # Выполняем все задачи параллельно
    try:
        analysis_id = db.add_analysis(analysis, user_id, prompt_id, transcription_id, tokens)
        logger.info(f"Анализ завершен.", extra={'user_id': user_id})
        return jsonify({"analysis_id": analysis_id, "analysis_text": analysis}), 200
    except Exception as e:
        logger.error(f"Ошибка в процессе параллельного анализа: {e}")
        return jsonify({'msg': 'Error processing analysis.'}), 500
    

@api_bp.route('/api/analysis/<analysis_id>', methods=['GET'])
@api_key_required
def get_analysis_by_id(analysis_id):
    # Получаем user_id, который был добавлен в декораторе
    user_id = request.user_id
    logger.info(f"Запрос на получение транскрипции по transcription_id: {analysis_id} для пользователя: {user_id}", extra={'user_id': user_id})
    from app.database.managers.analysis_manager import AnalysisManager
    
    db = AnalysisManager()
    analysis = db.get_analysis_by_id(analysis_id)
    prompt = get_prompt(analysis.prompt_id)
    transcription = get_transcription( analysis.transcription_id) 
    if analysis:
        return jsonify({
            'transcription_id': analysis.analysis_id,  # Убедитесь, что это поле существует
            'text': analysis.text,
            'prompt': prompt,
            'transcription': transcription,
            'tokens': analysis.tokens
        }), 200
    else:
        logger.warning("Анализ не найден.", extra={'user_id': user_id})
        return jsonify({"msg": "Analysis not found"}), 404
    

@api_bp.route('/api/analysis/all', methods=['GET'])
@api_key_required
def get_analysis():
    from app.database.managers.analysis_manager import AnalysisManager
    db = AnalysisManager()
    user_id = request.user_id
    offset = request.args.get('offset', default=0, type=int)  # Получаем offset из параметров запроса
    limit = request.args.get('limit', default=0, type=int)  # Получаем limit из параметров запроса
    logger.info(f"Запрос транскрипций для пользователя: {user_id} с offset={offset} и limit={limit}", extra={'user_id': user_id})
    analysis = db.get_analysis_by_user(user_id, offset, limit)
    if analysis:
        logger.info("Транскрипции найдены.", extra={'user_id': user_id})
        return jsonify(analysis), 200
    else:
        logger.warning("Транскрипции не найдены.", extra={'user_id': user_id})
        return jsonify({"msg": "No analysiss found"}), 404