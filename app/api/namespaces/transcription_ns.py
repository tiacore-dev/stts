from flask import request, jsonify, current_app
from flask_restx import Namespace, Resource
import logging
from app.utils.process_audio_api import process_and_transcribe_audio_1, process_and_transcribe_audio_2, check_channels
import os
from urllib.parse import urlparse, unquote
from app.utils.db_get import get_audio_name
import uuid
from app.decorators import api_key_required
from app.api.models import transcription_create_model_payload, transcription_create_model_response, transcription_model
import subprocess
from urllib.parse import urlparse, unquote
import uuid
from flask import jsonify
import requests

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


transcription_ns = Namespace('api/transcription', description='Schedule Details operations')
# Регистрируем модель в namespace
transcription_ns.models[transcription_create_model_payload.name] = transcription_create_model_payload
transcription_ns.models[transcription_create_model_response.name] = transcription_create_model_response
transcription_ns.models[transcription_model.name] = transcription_model

# Пример простого запроса
"""def test_http_request():
    try:
        logger.info("Отправка тестового запроса к внешнему сайту.")
        response = requests.get("https://www.google.com")
        
        if response.status_code == 200:
            logger.info("Запрос успешен, статус: 200")
        else:
            logger.error(f"Ошибка при запросе, статус: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке запроса: {e}")"""

@transcription_ns.route('/create')
class TranscriptionResource(Resource):
    @api_key_required
    @transcription_ns.expect(transcription_create_model_payload)
    @transcription_ns.marshal_with(transcription_create_model_response)
    def post(self):
        # Вызовем тестовую функцию
        #test_http_request()
        logger.info(f"Вход в метод TranscriptionResource.post ")
        from app.database.managers.audio_manager import AudioFileManager
        db = AudioFileManager()
        # Извлекаем данные из запроса
        audio_url = request.json.get('audio_url')
        new_filename = request.json.get('new_filename', None)
        prompt = request.json.get('prompt', None)

        user_id = request.user_id
        if not audio_url:
            return jsonify({"error": "Audio URL is required"}), 400

        try:
            # Загружаем файл с помощью requests и получаем его содержимое в память
            response = requests.get(audio_url)
            #, timeout=300

            # Проверяем статус ответа
            if response.status_code == 200:
                logger.info("Файл успешно загружен")
                audio_bytes = response.content  # Содержимое файла в памяти
            else:
                logger.error(f"Ошибка при загрузке файла: {response.text}")
                return jsonify({"error": "Ошибка при загрузке файла"}), 500
        except requests.RequestException as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            return jsonify({"error": f"Ошибка при выполнении запроса: {str(e)}"}), 400

        # Парсим URL и получаем путь без параметров
        parsed_url = urlparse(audio_url)
        path = parsed_url.path
        original_filename = os.path.basename(unquote(path))  # Декодируем URL

        # Извлекаем имя файла и расширение
        file_name, file_extension = os.path.splitext(original_filename)
        if not file_extension:
            file_extension = '.mp3'

        logger.info(f"Оригинальное название файла: {original_filename}")

        # Если новое имя файла передано, используем его, иначе оставляем оригинальное
        final_filename = new_filename if new_filename else file_name
        logger.info(f'Финальное название: {final_filename}')

        # Сохраняем аудиофайл в базе данных
        file_size = len(audio_bytes)  # Размер в байтах
        audio_id = db.add_audio_file(user_id, final_filename, file_extension, file_size, url=audio_url)

        logger.info(f"Полученное аудио с ID: {audio_id}")

        # Начинаем процесс транскрипции
        transcription_id = str(uuid.uuid4())
        """current_app.extensions['socketio'].emit('transcription_status', {
            'status': 'started', 
            'transcription_id': transcription_id, 
            'user_id': user_id,
            'filename': final_filename
        })"""
        
        # Определяем количество каналов в аудиофайле
        channels = check_channels(audio_bytes, file_extension)
        logger.info(f"Полученное число каналов: {channels}")
        
        if channels == 1:
            text = process_and_transcribe_audio_1(audio_bytes, user_id, audio_id, file_extension, transcription_id)
        elif channels == 2:
            text = process_and_transcribe_audio_2(audio_bytes, user_id, audio_id, file_extension, transcription_id, prompt)
        else:
            return jsonify({"error": "Invalid number of channels"}), 400
        # Возвращаем ID транскрипции и результат
        return {
            'transcription_id': transcription_id, 'transcription_text': text
        }



@transcription_ns.route('/<transcription_id>')
class TranscriptionResource(Resource):
    @api_key_required
    @transcription_ns.marshal_with(transcription_model)
    def get(self, transcription_id):
        # Получаем user_id, который был добавлен в декораторе
        user_id = request.user_id
        logger.info(f"Запрос на получение транскрипции по transcription_id: {transcription_id} для пользователя: {user_id}", extra={'user_id': user_id})
        from app.database.managers.transcription_manager import TranscriptionManager
        
        db = TranscriptionManager()
        transcription = db.get_transcription_by_id(transcription_id)

        if transcription:
            audio_file_name = get_audio_name(transcription.audio_id)
            return jsonify({
                'transcription_id': transcription.transcription_id,  # Убедитесь, что это поле существует
                'text': transcription.text,
                "audio_file_name": audio_file_name
                #'tokens': transcription.tokens
            }), 200
        else:
            logger.warning("Транскрипция не найдена.", extra={'user_id': user_id})
            return jsonify({"msg": "Transcription not found"}), 404
        

@transcription_ns.route('/all')
class TranscriptionResource(Resource):
    @api_key_required
    @transcription_ns.marshal_list_with(transcription_model)
    def get(self):
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

