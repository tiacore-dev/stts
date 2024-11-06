from app.database.db_setup import Base 
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Analysis(Base):
    __tablename__ = 'analysis'

    analysis_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)  # Внешний ключ
    text = Column(Text)
    prompt_id = Column(String(255), nullable=False)
    transcription_id = Column(String(255), nullable=False)
    tokens = Column(Integer)

    # Связи
    user = relationship("User", back_populates="analysis")


    def to_dict(self):
        return {
            "analysis_id": self.analysis_id,
            "user_id": self.user_id,
            "text": self.text,
            "prompt_id": self.prompt_id,
            "transcription_id": self.transcription_id, # Форматируем дату для JSON
            "tokens": self.tokens
        }