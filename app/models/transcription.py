from app.database.db_setup import Base 
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Transcription(Base):
    __tablename__ = 'transcriptions'

    transcription_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)  # Внешний ключ
    text = Column(Text)
    audio_id = Column(String(255), ForeignKey('audio_files.audio_id'), nullable=False)  # Внешний ключ
    tokens = Column(Integer)

    # Связи
    user = relationship("User", back_populates="transcriptions")
    audio_file = relationship("AudioFile")

    def to_dict(self):
        return {
            "transcription_id": self.transcription_id,
            "user_id": self.user_id,
            "text": self.text,
            "audio_id": self.audio_id,
            "tokens": self.tokens
        }