from pydub import AudioSegment
from app.openai.transcription import transcribe_audio
from app.openai.set_dialog import set_dialog
import io
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

def process_and_transcribe_audio(file_record, current_user, audio_id):
    from app.database.managers.transcription_manager import TranscriptionManager
    from app.s3 import get_s3_manager, get_bucket_name

    db = TranscriptionManager()
    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()

    filename = file_record.file_name
    file_extension = file_record.file_extension
    logger.info(f"Получен файл: {filename}, расширение: {file_extension}", extra={'user_id': current_user})

    # Скачиваем аудиофайл из S3
    audio_content = s3_manager.get_file(bucket_name, file_record.s3_key)
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_content), format=file_extension[1:])

    # Выполняем транскрибацию для всего аудио
    logger.info("Начало транскрибации всего аудио.", extra={'user_id': current_user})
    full_transcription = transcribe_audio(audio_content, file_extension)
    logger.info("Транскрибация всего аудио завершена.")

    # Разделяем аудио на два канала
    channels = audio_segment.split_to_mono()
    if len(channels) < 2:
        logger.warning("Аудиофайл имеет менее двух каналов. Выполняется транскрибация только одного канала.", extra={'user_id': current_user})
        channel1 = channels[0]
        channel2 = None  # Установите channel2 как None, если нет второго канала
    else:
        channel1 = channels[0]
        channel2 = channels[1]

    # Преобразуем каналы в байты для транскрибации
    channel1_bytes = io.BytesIO()
    channel1.export(channel1_bytes, format=file_extension[1:])

    # Выполняем транскрибацию для левого канала
    logger.info("Начало транскрибации левого канала.", extra={'user_id': current_user})
    channel1_transcription = transcribe_audio(channel1_bytes.getvalue(), file_extension)
    logger.info("Транскрибация левого канала завершена.")

    if channel2:  # Проверяем, существует ли второй канал
        logger.info("Начало транскрибации правого канала.", extra={'user_id': current_user})
        channel2_bytes = io.BytesIO()
        channel2.export(channel2_bytes, format=file_extension[1:])
        channel2_transcription = transcribe_audio(channel2_bytes.getvalue(), file_extension)
        logger.info("Транскрибация правого канала завершена.")
    else:
        channel2_transcription = None  # Если второго канала нет, присваиваем None


    # Анализируем текст и сохраняем транскрипции для пользователя
    logger.info("Анализ текста.", extra={'user_id': current_user})
    dialog, tokens_full = set_dialog(full_transcription, channel1_transcription, channel2_transcription)
    transcription_id = db.add_transcription(current_user, dialog, audio_id, tokens_full)
    
    return transcription_id
