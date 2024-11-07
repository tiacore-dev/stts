from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.forms import AudioForm
import logging
from app.utils.process_audio import process_and_transcribe_audio
import asyncio
from app.utils.db_get import get_audio_name
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



@transcription_bp.route('/transcription/all', methods=['GET'])
@jwt_required()
def get_transcriptions():
    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()
    current_user = get_jwt_identity()
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




@transcription_bp.route('/api/transcription/<transcription_id>', methods=['GET'])
@jwt_required()
def get_transcription_by_id(transcription_id):
    current_user = get_jwt_identity()
    logger.info(f"Запрос на получение транскрипции по transcription_id: {transcription_id} для пользователя: {current_user}", extra={'user_id': current_user})
    from app.database.managers.transcription_manager import TranscriptionManager
    
    db = TranscriptionManager()
    transcription = db.get_transcription_by_id(transcription_id)

    if transcription:
        return jsonify({
            'transcription_id': transcription.transcription_id,  # Убедитесь, что это поле существует
            'text': transcription.text,
            'analysis': transcription.analysis,
            'prompt': transcription.prompt,
            'tokens': transcription.tokens
        }), 200
    else:
        logger.warning("Транскрипция не найдена.", extra={'user_id': current_user})
        return jsonify({"msg": "Transcription not found"}), 404


@transcription_bp.route('/transcription/<transcription_id>/view', methods=['GET'])
@jwt_required()
def get_transcription_view(transcription_id):
    current_user = get_jwt_identity()
    logger.info(f"Запрос на отображение транскрипции с transcription_id: {transcription_id} для пользователя: {current_user}", extra={'user_id': current_user})
    
    # Передаем только transcription_id в шаблон
    return render_template('transcription/transcription_details.html', transcription_id=transcription_id)







@transcription_bp.route('/user_audio_files', methods=['GET'])
@jwt_required()
def get_user_audio_files():
    from app.database.managers.audio_manager import AudioFileManager
    audio_manager = AudioFileManager()
    current_user = get_jwt_identity()
    logger.info(f"Запрос аудиофайлов для пользователя: {current_user}", extra={'user_id': current_user['login']})
    audio_files = audio_manager.get_audio_files_by_user_for_transcription(current_user['user_id'])

    if audio_files:
        logger.info("Аудиофайлы найдены.", extra={'user_id': current_user['login']})
        logger.info(f"Найденные аудиофайлы: {audio_files}", extra={'user_id': current_user['login']})
        return jsonify({"audio_files": audio_files}), 200
    else:
        logger.warning("Аудиофайлы не найдены.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "No audio files found"}), 404






