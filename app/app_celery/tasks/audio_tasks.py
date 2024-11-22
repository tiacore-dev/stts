#from celery import app
from app.services.s3 import get_s3_manager, get_bucket_name
import logging
import os
from service_registry import get_service

celery=get_service('celery')


#file_path, user_id, file_name_input, login

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

@celery.task(name='process_and_upload_file_task')
def process_and_upload_file_task(file_path, user_id, file_name_input, login):
    logger.info('starting task')
    from app.database.managers.audio_manager import AudioFileManager
    db = AudioFileManager()
    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()

    file_extension = os.path.splitext(file_path)[1]
    full_file_name = f"{file_name_input}{file_extension}"
    s3_key = full_file_name.replace(' ', '_')
    file_size = os.path.getsize(file_path)  # Получаем размер файла из локальной системы

    try:
        # Сохраняем информацию о файле в БД
        audio_id = db.add_audio_file(user_id, file_name_input, file_extension, file_size, bucket_name, s3_key)

        # Загружаем файл в S3
        with open(file_path, 'rb') as file:
            s3_manager.upload_fileobj(file, bucket_name, audio_id + s3_key)

        # Удаляем локальный файл после загрузки
        os.remove(file_path)

        # Логируем успешную загрузку
        return {
            'status': 'success',
            'audio_id': audio_id,
            'file_name': file_name_input,
            's3_key': s3_key
        }

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при загрузке файла {file_name_input}: {e}", extra={'user_id': login})

        # Удаляем файл в случае ошибки, если он был создан
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            'status': 'error',
            'file_name': file_name_input,
            'error': str(e)
        }
