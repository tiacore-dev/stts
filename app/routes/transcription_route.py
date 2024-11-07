from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from app.utils.process_audio import process_and_transcribe_audio
import asyncio
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


transcription_bp = Blueprint('transcription', __name__)


@transcription_bp.route('/transcription/create', methods=['POST'])
@jwt_required()  # Убедитесь, что пользователь аутентифицирован
async def process_audio():
    from app.database.managers.audio_manager import AudioFileManager
    db_a = AudioFileManager()
    current_user = get_jwt_identity()
    audio_ids = request.json.get('audio_ids')  # Получаем список audio_id
    logger.info(f"Запрос транскрибации аудио с ID {audio_ids}", extra={'user_id': current_user['login']})

    # Проверка на отсутствие audio_id
    if not audio_ids or not isinstance(audio_ids, list):
        logger.warning("Отсутствуют audio_id.", extra={'user_id': current_user['login']})
        return jsonify({'msg': 'Missing audio IDs.'}), 400
    
    # Создаем задачи для каждой транскрипции
    tasks = []
    for audio_id in audio_ids:
        # Получаем информацию о файле из базы данных для каждого audio_id
        file_record = db_a.get_audio_file_by_id(current_user['user_id'], audio_id)
        if not file_record:
            logger.warning(f"Файл с ID {audio_id} не найден для пользователя {current_user}.", extra={'user_id': current_user['login']})
            continue
        # Добавляем задачу транскрипции
        tasks.append(process_and_transcribe_audio(file_record, current_user['user_id'], audio_id))
    logger.info(f"Начато транскрибирование.", extra={'user_id': current_user['login']})
    # Выполняем все задачи параллельно и ждем их завершения
    try:
        transcription_ids = await asyncio.gather(*tasks, return_exceptions=True)
        # Фильтруем исключения, чтобы отобразить только успешные транскрипции
        results = [{"audio_id": audio_id, "transcription_id": tid} 
                   for audio_id, tid in zip(audio_ids, transcription_ids) if not isinstance(tid, Exception)]
        logger.info(f"Транскрибирование завершено. Полученные id: {results}", extra={'user_id': current_user['login']})
        return jsonify({"transcriptions": results})
    except Exception as e:
        logger.error(f"Ошибка в процессе обработки аудио: {e}", extra={'user_id': current_user['login']})
        return jsonify({'msg': 'Error processing audio.'}), 500



@transcription_bp.route('/transcription/get_all', methods=['GET'])
@jwt_required()
def get_transcriptions():
    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()
    current_user = get_jwt_identity()
    offset = request.args.get('offset', default=0, type=int)  # Получаем offset из параметров запроса
    limit = request.args.get('limit', default=10, type=int)  # Получаем limit из параметров запроса
    logger.info(f"Запрос транскрипций для пользователя: {current_user} с offset={offset} и limit={limit}", extra={'user_id': current_user['login']})
    transcriptions = db.get_transcription_by_user(current_user['user_id'], offset, limit)
    
    if transcriptions:
        logger.info("Транскрипции найдены.", extra={'user_id': current_user['login']})
        return jsonify(transcriptions), 200
    else:
        logger.warning("Транскрипции не найдены.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "No transcriptions found"}), 404




@transcription_bp.route('/transcription/<transcription_id>/view', methods=['GET'])
@jwt_required()
def get_transcription_by_transcription_id(transcription_id):
    current_user = get_jwt_identity()
    logger.info(f"Запрос на получение транскрипции по transcription_id: {transcription_id} для пользователя: {current_user}", extra={'user_id': current_user['login']})
    from app.database.managers.transcription_manager import TranscriptionManager
    
    db = TranscriptionManager()
    transcription = db.get_transcription_by_id(transcription_id)

    if transcription:
        return jsonify(transcription), 200
    else:
        logger.warning("Транскрипция не найдена.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "Transcription not found"}), 404





@transcription_bp.route('/user_prompts', methods=['GET'])
@jwt_required()
def get_user_prompts():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()
    
    logger.info(f"Запрос готовых промптов для пользователя: {current_user}", extra={'user_id': current_user['login']})
    prompts = prompt_manager.get_prompts_by_user(current_user['user_id'])  # Извлекаем промпты для текущего пользователя
    prompt_data = []
    for s in prompts:
        prompt_info = {
            "prompt_name": s[0]
        }
        
        prompt_data.append(prompt_info)
    if prompt_data:
        return jsonify(prompt_data=prompt_data), 200
    else:
        return jsonify({"msg": "No prompts found"}), 404


@transcription_bp.route('/user_audio_files', methods=['GET'])
@jwt_required()
def get_user_audio_files():
    from app.database.managers.audio_manager import AudioFileManager
    audio_manager = AudioFileManager()
    current_user = get_jwt_identity()
    logger.info(f"Запрос аудиофайлов для пользователя: {current_user}", extra={'user_id': current_user['login']})
    audio_files = audio_manager.get_audio_files_by_user(current_user['user_id'])

    if audio_files:
        logger.info("Аудиофайлы найдены.", extra={'user_id': current_user['login']})
        return jsonify(audio_files=audio_files), 200
    else:
        logger.warning("Аудиофайлы не найдены.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "No audio files found"}), 404



@transcription_bp.route('/get_automatic_prompt', methods=['GET'])
@jwt_required()
def get_automatic_prompt():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()

    # Получаем автоматический промпт
    automatic_prompt = prompt_manager.get_automatic_prompt(current_user['user_id'])

    if automatic_prompt:
        logger.info(f"Автоматический промпт найден и отправлен пользователю {current_user}", extra={'user_id': current_user['login']})
        return jsonify(automatic_prompt), 200  # Возвращаем полные данные о промпте
    else:
        return jsonify({"msg": "No automatic prompt found"}), 404


