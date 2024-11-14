from app.models.api_keys import APIKeys
import uuid
from app.database.db_globals import Session
import uuid
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

class APIKeysManager:
    def __init__(self):
        self.Session = Session

    def add_api_key(self, user_id, comment):
        """Добавление API key."""
        session = self.Session()
        api_key = str(uuid.uuid4())
        key_id = str(uuid.uuid4())
        new_record = APIKeys(key_id=key_id, api_key=api_key, user_id=user_id, comment=comment)  # Создаем объект APIKey
        session.add(new_record)  # Добавляем новый лог через сессию
        session.commit()  # Не забудьте зафиксировать изменения в базе данных
        return api_key
    

    def delete_api_key(self, key_id):
        session = self.Session()
        logger.info(f"Удаление аудиофайла '{key_id}' из базы данных.", extra={'user_id': 'APIKeysManager'})
        try:
            # Найдите файл в базе данных по имени
            file_to_delete = session.query(APIKeys).filter_by(key_id=key_id).first()
            if file_to_delete:
                session.delete(file_to_delete)
                session.commit()
                logger.info(f"Аудиофайл '{key_id}' успешно удален из базы данных.", extra={'user_id': 'APIKeysManager'})
                return True
            else:
                logger.warning(f"Аудиофайл '{key_id}' не найден в базе данных.", extra={'user_id': 'APIKeysManager'})
                return False
        except Exception as e:
            logger.error(f"Ошибка при удалении аудиофайла '{key_id}': {e}", extra={'user_id': 'APIKeysManager'})
            session.rollback()
            return False
        finally:
            session.close()

    def get_api_keys(self, user_id):
        session = self.Session()
        try:
            logger.info(f"Получение ключей для пользователя: {user_id}", extra={'user_id': 'PromptManager'})
            api_keys = session.query(APIKeys).filter_by(user_id=user_id).all()
            result = [a.to_dict() for a in api_keys]
        finally:
            session.close()
        return result
    
    def get_user_by_api_key(self, api_key):
        session = self.Session()
        try:
            logger.info(f"Получение пользователя по ключу", extra={'user_id': 'PromptManager'})
            api_key = session.query(APIKeys).filter_by(api_key=api_key).first()
            return api_key.user_id
        finally:
            session.close()
        