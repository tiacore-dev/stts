from app.models.analysis import Analysis
import uuid
from app.database.db_globals import Session
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


class AnalysisManager:
    def __init__(self):
        self.Session = Session

    def add_analysis(self, text, user_id, prompt_id, transcription_id,  tokens):
        session = self.Session()
        logger.info("Сохранение анализа в базу данных.", extra={'user_id': 'AnalysisManager'})
        analysis_id = uuid.uuid4()
        new_analysis = Analysis(analysis_id=analysis_id,
                                          user_id=user_id,                                           
                                           text=text,
                                           prompt_id=prompt_id,
                                           transcription_id=transcription_id,
                                           tokens=tokens)
        session.add(new_analysis)
        session.commit()
        session.close()
        logger.info("Анализ успешно сохранен.", extra={'user_id': user_id})
        return analysis_id
    

    def get_analysis_by_user(self, user_id, offset=0, limit=10):
        session = self.Session()
        try:
            logger.info(f"Получение анализа для пользователя: {user_id} с ограничением {limit} и смещением {offset}.", extra={'user_id': user_id})
            analysis = session.query(Analysis).filter_by(user_id=user_id).limit(limit).offset(offset).all()
            result = [{
                'analysis_id': t.analysis_id,  
                'text': t.text,
                'prompt_id': t.prompt_id,      
                'transcription_id': t.transcription_id,          
                'tokens': t.tokens
            } for t in analysis]
        finally:
            session.close()
        return result
    

    def get_analysis_by_id(self, analysis_id):
        session = self.Session()
        try:
            
            analysis = session.query(Analysis).filter_by(analysis_id=analysis_id).first()
            user_id = analysis.user_id
            logger.info(f"Получение анализаи по analysis_id: {analysis_id}", extra={'user_id': user_id})
            return analysis.to_dict()
        finally:
            session.close()
        