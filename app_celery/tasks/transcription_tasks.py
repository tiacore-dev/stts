#from celery import app
from app.services.openai.transcription import transcribe_audio
from app.services.openai.set_dialog import set_dialog
from app.services.s3 import get_s3_manager, get_bucket_name
import io
from pydub import AudioSegment
import logging
from app.utils.db_get import transcribed_audio
from celery import shared_task
#from app_celery import get_celery_app

#celery = get_celery_app()

logger = logging.getLogger('chatbot')

logger.info("Task module loaded and registered")

#audio_id, user_id, login
#@celery.task(name='process_and_transcribe_audio_task')
@shared_task
def process_and_transcribe_audio_task(audio_id, user_id, login):
    logger.info(f"Received parameters - audio_id: {audio_id}, user_id: {user_id}, login: {login}")

    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()
    from app.database.managers.audio_manager import AudioFileManager
    db_a = AudioFileManager()
    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()
    
    file_record = db_a.get_audio_by_id(audio_id)
    if not file_record:
        logger.warning(f"Файл с ID {audio_id} не найден для пользователя {login}.", extra={'user_id': login})
        return None

    # Используем asyncio для синхронного выполнения асинхронной функции
    audio_content = s3_manager.get_file(bucket_name, audio_id + file_record['s3_key'])
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_content), format=file_record['file_extension'][1:])

    # Выполнение транскрибации
    tasks = []
    tasks.append(transcribe_audio(audio_content, file_record['file_extension']))

    channels = audio_segment.split_to_mono()
    channel1, channel2 = channels[0], channels[1] if len(channels) > 1 else None

    # Транскрибация левого канала
    channel1_bytes = io.BytesIO()
    channel1.export(channel1_bytes, format=file_record['file_extension'][1:])
    tasks.append(transcribe_audio(channel1_bytes.getvalue(), file_record['file_extension']))

    # Транскрибация правого канала, если существует
    if channel2:
        channel2_bytes = io.BytesIO()
        channel2.export(channel2_bytes, format=file_record['file_extension'][1:])
        tasks.append(transcribe_audio(channel2_bytes.getvalue(), file_record['file_extension']))

    # Сбор результатов транскрибации
    transcriptions = [t if not isinstance(t, Exception) else None for t in tasks]
    dialog, tokens_full = set_dialog(*transcriptions)

    # Добавление транскрипции в базу данных
    transcription_id = db.add_transcription(user_id, dialog, audio_id, tokens_full)
    
    # Установление статуса транскрибации
    is_set = transcribed_audio(audio_id)
    if is_set:
        logger.info(f"Установлена транскрибированность для аудио с ID: {audio_id}", extra={'user_id': login})
    else:
        logger.error(f"Ошибка установления транскрибированности для аудио с ID: {audio_id}", extra={'user_id': login})

    return transcription_id
