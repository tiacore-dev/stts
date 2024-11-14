# app/utils/process_audio.py
from pydub import AudioSegment
from app.services.openai.transcription import transcribe_audio
from app.services.openai.set_dialog import set_dialog
import io
import logging

from app.utils.db_get import transcribed_audio

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

def process_and_transcribe_audio(file_record, current_user, audio_id):
    from app.database.managers.transcription_manager import TranscriptionManager
    from app.services.s3 import get_s3_manager, get_bucket_name

    db = TranscriptionManager()
    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()

    filename = file_record['file_name']
    file_extension = file_record['file_extension']
    logger.info(f"Получен файл: {filename}, расширение: {file_extension}", extra={'user_id': current_user})

    # Скачиваем аудиофайл из S3
    audio_content = s3_manager.get_file(bucket_name, file_record['s3_key'])
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_content), format=file_extension[1:])
    transcriptions = []
    # Выполняем транскрибацию для всего аудио
    logger.info("Начало транскрибации всего аудио.", extra={'user_id': current_user})
    transcriptions.append(transcribe_audio(audio_content, file_extension))

    # Разделяем аудио на два канала
    channels = audio_segment.split_to_mono()
    if len(channels) < 2:
        logger.warning("Аудиофайл имеет менее двух каналов. Выполняется транскрибация только одного канала.", extra={'user_id': current_user})
        channel1 = channels[0]
        channel2 = None  # Установите channel2 как None, если нет второго канала
    else:
        channel1, channel2 = channels[0], channels[1]

    # Преобразуем каналы в байты для транскрибации
    channel1_bytes = io.BytesIO()
    channel1.export(channel1_bytes, format=file_extension[1:])
    channel1_bytes_value = channel1_bytes.getvalue()

    # Создаем задачу для транскрибации левого канала
    logger.info("Начало транскрибации левого канала.", extra={'user_id': current_user})
    transcriptions.append(transcribe_audio(channel1_bytes_value, file_extension))

    # Создаем задачу для транскрибации правого канала, если он существует
    if channel2:
        logger.info("Начало транскрибации правого канала.", extra={'user_id': current_user})
        channel2_bytes = io.BytesIO()
        channel2.export(channel2_bytes, format=file_extension[1:])
        channel2_bytes_value = channel2_bytes.getvalue()
        transcriptions.append(transcribe_audio(channel2_bytes_value, file_extension))
    else:
        channel2_transcription_task = None

    
    for i, transcription in enumerate(transcriptions):
        if isinstance(transcription, Exception):
            logger.error(f"Ошибка транскрибации для канала {i + 1}: {transcription}", extra={'user_id': current_user})
            transcriptions[i] = None  # Преобразуем ошибку в None
        else:
            logger.info(f"Транскрибация для канала {i + 1}: {transcription[:100]}...", extra={'user_id': current_user})

    # Анализируем текст и сохраняем транскрипции для пользователя
    logger.info("Анализ текста.", extra={'user_id': current_user})
    dialog, tokens_full = set_dialog(transcriptions[0], transcriptions[1], transcriptions[2])
    transcription_id = db.add_transcription(current_user, dialog, audio_id, tokens_full)
    """is_set = transcribed_audio(audio_id)
    if is_set:
        logger.info(f"Установлена транскрибированность для аудио с ID: {audio_id}", extra={'user_id': current_user})
    else:
        logger.error(f"Ошибка установления транскрибированности для аудио с ID: {audio_id}", extra={'user_id': current_user})"""
    logger.info(f"Получена транскрипция с ID: {transcription_id}", extra={'user_id': current_user})
    return str(transcription_id)  # Возвращаем transcription_id как строку
