import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

async def process_and_upload_file(file, s3_key, current_user, file_name_input, file_extension, file_size):
    from app.database.managers.audio_manager import AudioFileManager
    from app.services.s3 import get_s3_manager, get_bucket_name

    db = AudioFileManager()
    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()
     # Получаем асинхронный менеджер S3
    try:
        # Загружаем файл в S3 асинхронно
        await s3_manager.upload_fileobj(file, bucket_name, s3_key)
        
        # Сохраняем информацию о файле в БД
        audio_id = db.add_audio_file(current_user['user_id'], file_name_input, file_extension, file_size, bucket_name, s3_key)
        
        # Логируем успешную загрузку
        return {
            'status': 'success',
            'audio_id': audio_id,
            'file_name': file_name_input,
            's3_key': s3_key
        }
    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при загрузке файла {file_name_input}: {e}", extra={'user_id': current_user['login']})
        return {
            'status': 'error',
            'file_name': file_name_input,
            'error': str(e)
        }