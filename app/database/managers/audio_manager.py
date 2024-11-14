from sqlalchemy import exists
from app.models.audio import AudioFile
import uuid
from app.database.db_globals import Session
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

class AudioFileManager:
    def __init__(self):
        self.Session = Session

    def add_audio_file(self, user_id, file_name, file_extension, file_size, bucket_name=None, s3_key=None, url=None, transcribed=False):
        session = self.Session()
        logger.info(f"Сохранение информации о загруженном аудиофайле '{file_name}' для пользователя '{user_id}'.", extra={'user_id': 'AudioManager'})
        audio_id = str(uuid.uuid4())
        try:
            new_file = AudioFile(
                audio_id=audio_id,
                user_id=user_id,
                file_name=file_name,
                file_extension=file_extension,
                file_size=file_size,
                bucket_name=bucket_name,
                s3_key=s3_key,
                url=url,
                transcribed=transcribed
            )
            session.add(new_file)
            session.commit()
            logger.info(f"Аудиофайл '{file_name}' успешно сохранен в базе данных.", extra={'user_id': 'AudioManager'})
            return audio_id
        except Exception as e:
            logger.error(f"Ошибка при сохранении аудиофайла '{file_name}': {e}", extra={'user_id': 'AudioManager'})
            session.rollback()
        finally:
            session.close()

    def get_audio_files_by_user(self, user_id):
        session = self.Session()
        logger.info(f"Получение списка аудиофайлов для пользователя '{user_id}'.", extra={'user_id': 'AudioManager'})
        try:
            # Логируем перед выполнением запроса
            files = session.query(AudioFile).filter_by(user_id=user_id).all()
            logger.info(f"Запрос к БД выполнен. Найдено файлов: {len(files)}", extra={'user_id': 'AudioManager'})

            if not files:
                logger.warning(f"Для пользователя '{user_id}' не найдено аудиофайлов.", extra={'user_id': 'AudioManager'})
            
            # Формируем массив массивов
            result = [[f.audio_id, f.file_name, f.bucket_name, f.s3_key, f.transcribed] for f in files]
            return result
        except Exception as e:
            logger.error(f"Ошибка при запросе аудиофайлов: {e}", extra={'user_id': 'AudioManager'})
            raise e
        finally:
            session.close()


    def get_audio_file_by_name(self,user_id, file_name):
        session = self.Session()
        logger.info(f"Получение аудиофайла по ID '{file_name}'.", extra={'user_id': 'AudioManager'})
        try:
            file = session.query(AudioFile).filter_by(user_id=user_id, file_name=file_name).first()
            if file:
                logger.info(f"Аудиофайл '{file.file_name}' найден.", extra={'user_id': 'AudioManager'})
            else:
                logger.warning(f"Аудиофайл с ID '{file_name}' не найден.", extra={'user_id': 'AudioManager'})
            return file
        finally:
            session.close()

    def delete_audio_file(self, audio_id):
        session = self.Session()
        logger.info(f"Удаление аудиофайла '{audio_id}' из базы данных.", extra={'user_id': 'AudioManager'})
        try:
            # Найдите файл в базе данных по имени
            file_to_delete = session.query(AudioFile).filter_by(audio_id=audio_id).first()
            if file_to_delete:
                session.delete(file_to_delete)
                session.commit()
                logger.info(f"Аудиофайл '{audio_id}' успешно удален из базы данных.", extra={'user_id': 'AudioManager'})
                return True
            else:
                logger.warning(f"Аудиофайл '{audio_id}' не найден в базе данных.", extra={'user_id': 'AudioManager'})
                return False
        except Exception as e:
            logger.error(f"Ошибка при удалении аудиофайла '{audio_id}': {e}", extra={'user_id': 'AudioManager'})
            session.rollback()
            return False
        finally:
            session.close()


    def get_audio_file_by_id(self,user_id, audio_id):
        session = self.Session()
        logger.info(f"Получение аудиофайла по ID '{audio_id}'.", extra={'user_id': 'AudioManager'})
        try:
            file = session.query(AudioFile).filter_by(user_id=user_id, audio_id=audio_id).first()
            if file:
                logger.info(f"Аудиофайл '{file.audio_id}' найден.", extra={'user_id': 'AudioManager'})
            else:
                logger.warning(f"Аудиофайл с ID '{audio_id}' не найден.", extra={'user_id': 'AudioManager'})
            return file
        finally:
            session.close()


    def get_audio_by_id(self, audio_id):
        session = self.Session()
        logger.info(f"Получение названия аудиофайла по ID '{audio_id}'.", extra={'user_id': 'AudioManager'})
        try:
            file = session.query(AudioFile).filter_by(audio_id=audio_id).first()
            if file:
                logger.info(f"Аудиофайл '{file.audio_id}' найден.", extra={'user_id': 'AudioManager'})
            else:
                logger.warning(f"Аудиофайл с ID '{audio_id}' не найден.", extra={'user_id': 'AudioManager'})
            return file.to_dict()
        finally:
            session.close()
    

    def get_audio_files_by_user_for_transcription(self, user_id):
        session = self.Session()
        logger.info(f"Получение списка аудиофайлов для пользователя '{user_id}'.", extra={'user_id': 'AudioManager'})
        try:
            files = session.query(AudioFile).filter_by(user_id=user_id, transcribed=False).all()
            logger.info(f"Найдено {len(files)} аудиофайлов для пользователя '{user_id}'.", extra={'user_id': 'AudioManager'})
            
            # Возвращаем простой список словарей, без вложенных массивов
            result = [f.to_dict() for f in files]
            return result
        finally:
            session.close()

    def set_transcribed_audio(self, audio_id):
        session = self.Session()
        logger.info(f"Получение аудиофайла по ID '{audio_id}'.", extra={'user_id': 'AudioManager'})
        try:
            file = session.query(AudioFile).filter_by(audio_id=audio_id).first()
            if file:
                logger.info(f"Аудиофайл '{file.audio_id}' найден.", extra={'user_id': 'AudioManager'})
                file.transcribed=True
                session.commit()
                return True
            else:
                logger.warning(f"Аудиофайл с ID '{audio_id}' не найден.", extra={'user_id': 'AudioManager'})
                return False
        except Exception as e:
            logger.error(f"Ошибка при установке транскрибированности аудиофайла '{audio_id}': {e}", extra={'user_id': 'AudioManager'})
            session.rollback()
            return False
        finally:
            session.close()

    