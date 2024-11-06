from sqlalchemy import exists
from flask import current_app
from app.models.transcription import Transcription
import uuid
from app.database.db_globals import Session
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


class TranscriptionManager:
    def __init__(self):
        self.Session = Session

    def add_transcription(self,  user_id,text, audio_id, tokens):
        session = self.Session()
        logger.info("Сохранение транскрипции в базу данных.", extra={'user_id': user_id})
        transcription_id = uuid.uuid4()
        new_transcription = Transcription(transcription_id=transcription_id,
                                          user_id=user_id,                                           
                                           text=text,
                                           audio_id=audio_id,
                                           tokens=tokens)
        session.add(new_transcription)
        session.commit()
        session.close()
        logger.info("Транскрипция успешно сохранена.", extra={'user_id': user_id})
        return transcription_id

    def get_transcription_by_user(self, user_id, offset=0, limit=10):
        session = self.Session()
        try:
            logger.info(f"Получение транскрипций для пользователя: {user_id} с ограничением {limit} и смещением {offset}.", extra={'user_id': user_id})
            transcriptions = session.query(Transcription).filter_by(user_id=user_id).limit(limit).offset(offset).all()
            result = [{
                'transcription_id': t.transcription_id,  # Добавлено поле transcription_id
                'text': t.text,
                'audio_id': t.audio_id,                
                'tokens': t.tokens
            } for t in transcriptions]
        finally:
            session.close()
        return result



    def get_transcription_by_id(self, transcription_id):
        session = self.Session()
        try:
            
            transcription = session.query(Transcription).filter_by(transcription_id=transcription_id).first()
            user_id=transcription.user_id
            logger.info(f"Получение транскрипции по transcription_id: {transcription_id}", extra={'user_id': user_id})
            return transcription.to_dict()
        finally:
            session.close()
        



    def get_transcription_by_audio_id(self, user_id, audio_id):
        session = self.Session()
        try:
            logger.info(f"Получение транскрипции по audio_id: {audio_id}", extra={'user_id': user_id})
            transcription = session.query(Transcription).filter_by(user_id=user_id, audio_id=audio_id).first()
            
            if transcription:
                return transcription.to_dict()
            else:
                return None  # Если транскрипция не найдена, возвращаем None
        finally:
            session.close()

