import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

def process_and_upload_file(file, current_user, file_name_input, user_login):
    from app.database.managers.audio_manager import AudioFileManager
    from app.services.s3 import get_s3_manager, get_bucket_name

    db = AudioFileManager()
    s3_manager = get_s3_manager()
    bucket_name = get_bucket_name()
    
    file_extension = file.filename.split('.')[-1]  # Получаем расширение файла
    file_size = len(file.read())  # Получаем размер файла (после чтения его содержимого)

    # Сбрасываем указатель на начало файла после чтения
    file.seek(0)

    try:

        s3_key = f"{current_user}/{file_name_input}.{file_extension}"
        audio_id = db.add_audio_file(current_user, file_name_input, file_extension, file_size, bucket_name, s3_key)

        # Загружаем файл в S3 асинхронно
        
        s3_manager.upload_fileobj(file, bucket_name, s3_key)
        

        
        
        # Логируем успешную загрузку
        return {
            'status': 'success',
            'audio_id': audio_id,
            'file_name': file_name_input,
            's3_key': s3_key
        }
    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при загрузке файла {file_name_input}: {e}", extra={'user_id': user_login})
        return {
            'status': 'error',
            'file_name': file_name_input,
            'error': str(e)
        }
