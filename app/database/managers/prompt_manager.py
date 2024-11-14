from sqlalchemy import exists
from app.models.prompt import Prompt
import uuid
from app.database.db_globals import Session
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


class PromptManager:
    def __init__(self):
        self.Session = Session

    def add_prompt(self, user_id, prompt_name, text, use_automatic=False):
        session = self.Session()
        logger.info("Сохранение промпта в базу данных.", extra={'user_id': 'PromptManager'})
        prompt_id = str(uuid.uuid4())
        new_prompt = Prompt(prompt_id=prompt_id, user_id=user_id, prompt_name=prompt_name, text=text, use_automatic=use_automatic)
        session.add(new_prompt)
        session.commit()
        session.close()
        logger.info("Промпт успешно сохранен.", extra={'user_id': 'PromptManager'})
        return prompt_id

    def get_prompts_by_user(self, user_id):
        session = self.Session()
        try:
            logger.info(f"Получение промптов для пользователя: {user_id}", extra={'user_id': 'PromptManager'})
            prompts = session.query(Prompt).filter_by(user_id=user_id).all()
            result = [[p.prompt_name, p.text, p.prompt_id, p.use_automatic] for p in prompts]
        finally:
            session.close()
        return result
    
    def get_prompt_by_prompt_id(self,  prompt_id):
        session = self.Session()
        try:
            logger.info(f"Получение промпта по prompt_id: {prompt_id}", extra={'user_id': 'PromptManager'})
            prompt = session.query(Prompt).filter_by( prompt_id=prompt_id).first()
        finally:
            session.close()
        return prompt.to_dict()

    def get_prompt_by_prompt_name(self, user_id, prompt_name):
        session = self.Session()
        try:
            logger.info(f"Получение промпта по prompt_id: {prompt_name}", extra={'user_id': 'PromptManager'})
            prompt = session.query(Prompt).filter_by(user_id=user_id, prompt_name=prompt_name).first()
            return prompt.to_dict()
        finally:
            session.close()
        

    def edit_prompt(self, prompt_id, new_text, new_prompt_name):
        session = self.Session()
        try:
            logger.info(f"Редактирование промпта '{prompt_id}'", extra={'user_id': 'PromptManager'})
            prompt = session.query(Prompt).filter_by(prompt_id=prompt_id).first()
            if prompt:
                prompt.text = new_text
                prompt.prompt_name = new_prompt_name  # Обновляем имя промпта
                session.commit()
                logger.info(f"Промпт '{prompt_id}' обновлен ", extra={'user_id': 'PromptManager'})
                return True  # Успешное редактирование
            else:
                logger.warning(f"Промпт '{prompt_id}' не найден", extra={'user_id': 'PromptManager'})
                return False  # Промпт не найден
        except Exception as e:
            logger.error(f"Ошибка при редактировании промпта: {e}", extra={'user_id': 'PromptManager'})
            session.rollback()
            raise e
        finally:
            session.close()



    def delete_prompt(self, prompt_id):
        session = self.Session()
        try:
            logger.info(f"Удаление промпта '{prompt_id}'", extra={'user_id': 'PromptManager'})
            prompt = session.query(Prompt).filter_by(prompt_id=prompt_id).first()
            if prompt:
                session.delete(prompt)
                session.commit()
                logger.info(f"Промпт '{prompt_id}' успешно удален.", extra={'user_id': 'PromptManager'})
            else:
                logger.warning(f"Промпт '{prompt_id}' не найден", extra={'user_id': 'PromptManager'})
        except Exception as e:
            logger.error(f"Ошибка при удалении промпта: {e}", extra={'user_id': 'PromptManager'})
            session.rollback()
            raise e
        finally:
            session.close()


    def get_automatic_prompt(self, user_id):
        session = self.Session()
        try:
            logger.info(f"Поиск автоматического промпта для пользователя: {user_id}", extra={'user_id': 'PromptManager'})
            prompt = session.query(Prompt).filter_by(user_id=user_id, use_automatic=True).first()  # Получаем первый промпт с флагом use_automatic=True
            
            # Возвращаем всю информацию о промпте, если он найден
            if prompt:
                logger.info(f"Автоматический промпт '{prompt.prompt_name}' найден для пользователя: {user_id}", extra={'user_id': 'PromptManager'})
                return prompt.to_dict()
            else:
                logger.info(f"Автоматический промпт не найден для пользователя: {user_id}", extra={'user_id': 'PromptManager'})
                return None
        except Exception as e:
            logger.error(f"Ошибка при поиске автоматического промпта: {e}", extra={'user_id': 'PromptManager'})
            raise e
        finally:
            session.close()

        

    def reset_automatic_flag(self, user_id):
        logger.info(f"Сброс флага 'use_automatic' для всех промптов пользователя {user_id}.")
        session = self.Session()
        try:
            prompts = session.query(Prompt).filter_by(user_id=user_id, use_automatic=True).all()
            for prompt in prompts:
                prompt.use_automatic = False
            session.commit() 
            logger.info(f"Флаг 'use_automatic' сброшен для {len(prompts)} промптов пользователя {user_id}.")
        except Exception as e:
            logger.error(f"Ошибка при сбросе флага 'use_automatic' для пользователя {user_id}: {e}")
            session.rollback()
            raise e
        finally:
            session.close()
            logger.info(f"Сессия для сброса флагов 'use_automatic' для пользователя {user_id} закрыта.")


    def set_automatic_flag(self, prompt_id, use_automatic):
        logger.info(f"Установка флага 'use_automatic' для промпта ID: {prompt_id} на {use_automatic}.")
        session = self.Session()
        try:
            prompt = session.query(Prompt).filter_by(prompt_id=prompt_id).first()
            if prompt:
                prompt.use_automatic = use_automatic
                session.commit()
                logger.info(f"Флаг 'use_automatic' для промпта ID: {prompt_id} успешно обновлён на {use_automatic}.")
            else:
                logger.warning(f"Промпт ID: {prompt_id} не найден.")
                raise ValueError(f"Prompt with ID {prompt_id} not found")
        except Exception as e:
            logger.error(f"Ошибка при установке флага 'use_automatic' для промпта ID: {prompt_id}: {e}")
            session.rollback()
            raise e
        finally:
            session.close()
            logger.info(f"Сессия для установки флага 'use_automatic' для промпта ID: {prompt_id} закрыта.")
