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
        api_key = uuid.uuid4()
        new_record = APIKeys(api_key=api_key, user_id=user_id, comment=comment)  # Создаем объект APIKey
        session.add(new_record)  # Добавляем новый лог через сессию
        session.commit()  # Не забудьте зафиксировать изменения в базе данных
        return api_key
    
    def refresh_api_key(self, user_id, new_comment):
        session = self.Session()
        new_api_key = uuid.uuid4()
        logger.info(f"Обновление api_key для пользователя '{user_id}'.", extra={'user_id': 'APIKeyManager'})
        try:
            # Находим api_key по user_id
            api_key_record = session.query(APIKeys).filter_by(user_id=user_id).first()
            
            if api_key_record:
                # Обновляем api_key
                api_key_record.api_key = new_api_key
                api_key_record.comment = new_comment
                session.commit()  # Сохраняем изменения в базе данных
                logger.info(f"api_key для пользователя '{user_id}' успешно обновлён.", extra={'user_id': 'APIKeyManager'})
                return new_api_key
            else:
                logger.warning(f"api_key для пользователя '{user_id}' не найден.", extra={'user_id': 'APIKeyManager'})
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении api_key для пользователя '{user_id}': {str(e)}", extra={'user_id': 'APIKeyManager'})
            session.rollback()  # Откатываем изменения в случае ошибки
            
        finally:
            session.close()

