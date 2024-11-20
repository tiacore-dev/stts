# app/utils/process_audio.py
from pydub import AudioSegment
from app.services.openai.transcription import transcribe_audio
from app.services.openai.set_dialog import set_dialog
import io
import logging
import json
from app.utils.db_get import transcribed_audio
from service_registry import get_service


socket = get_service('sockets')

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

def check_channels(file_record, file_extension):
    audio_segment = AudioSegment.from_file(io.BytesIO(file_record), format=file_extension[1:])
    channels = audio_segment.split_to_mono()
    return len(channels)

def process_and_transcribe_audio_1(file_record, user_id, audio_id, file_extension, transcription_id):
    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()

    logger.info("Начало транскрибации аудио.", extra={'user_id': user_id})
    transcription = transcribe_audio(file_record, file_extension)
    transcription_id = db.add_transcription_with_id(transcription_id, user_id, transcription, audio_id, tokens=None)
    """socket.send(json.dumps({
        'status': 'completed',
        'transcription_id': transcription_id,
        'user_id': user_id
    }))"""
    return transcription


def process_and_transcribe_audio_2(file_record, user_id, audio_id, file_extension, transcription_id, prompt):
    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()

    audio_segment = AudioSegment.from_file(io.BytesIO(file_record), format=file_extension[1:])
    transcriptions = []
    
    # Выполняем транскрибацию для всего аудио
    logger.info("Начало транскрибации всего аудио.", extra={'user_id': user_id})
    transcriptions.append(transcribe_audio(file_record, file_extension))
    """socket.send(json.dumps({
        'status': 'in_progress',
        'stage': 'main_audio_processed',
        'transcription_id': transcription_id,
        'user_id': user_id
    }))"""
    # Стартовая отправка сообщения через WebSocket
    
    # Разделяем аудио на два канала
    channels = audio_segment.split_to_mono()
    channel1, channel2 = channels[0], channels[1]

    # Преобразуем каналы в байты для транскрибации
    channel1_bytes = io.BytesIO()
    channel2_bytes = io.BytesIO()
    channel1.export(channel1_bytes, format=file_extension[1:])
    channel2.export(channel2_bytes, format=file_extension[1:])
    channel1_bytes_value = channel1_bytes.getvalue()
    channel2_bytes_value = channel2_bytes.getvalue()

    # Создаем задачу для транскрибации левого канала
    logger.info("Начало транскрибации левого канала.", extra={'user_id': user_id})
    transcriptions.append(transcribe_audio(channel1_bytes_value, file_extension))
    # Прогресс (например, после завершения обработки канала 1)
    """socket.send(json.dumps({
        'status': 'in_progress',
        'stage': 'channel_1_processed',
        'transcription_id': transcription_id,
        'user_id': user_id
    }))"""
    transcriptions.append(transcribe_audio(channel2_bytes_value, file_extension))
    # Прогресс (например, после завершения обработки канала 1)
    # Отправка обновления прогресса для канала 2
    """socket.send(json.dumps({
        'status': 'in_progress',
        'stage': 'channel_2_processed',
        'transcription_id': transcription_id,
        'user_id': user_id
    }))"""

    
    for i, transcription in enumerate(transcriptions):
        if isinstance(transcription, Exception):
            logger.error(f"Ошибка транскрибации для канала {i + 1}: {transcription}", extra={'user_id': user_id})
            transcriptions[i] = None  # Преобразуем ошибку в None
        else:
            logger.info(f"Транскрибация для канала {i + 1}: {transcription[:100]}...", extra={'user_id': user_id})

    # Анализируем текст и сохраняем транскрипции для пользователя
    logger.info("Составление диалога.", extra={'user_id': user_id})
    dialog, tokens_full = set_dialog(transcriptions[0], transcriptions[1], transcriptions[2], prompt)
    transcription_id = db.add_transcription_with_id(transcription_id, user_id, dialog, audio_id, tokens_full)
    logger.info(f"Получена транскрипция с ID: {transcription_id}", extra={'user_id': user_id})
    # Завершение задачи
    return dialog 
    """socket.send(json.dumps({
        'status': 'completed',
        'transcription_id': transcription_id,
        'user_id': user_id
    }))"""
     


