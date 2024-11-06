from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db_setup import Base 
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True, autoincrement=False)
    username = Column(String) # Имя пользователя
    login = Column(String, unique=True, nullable=False)  # Email или логин
    password_hash = Column(String, nullable=True)  # Может быть NULL для OAuth-пользователей
    user_type = Column(String, default='user') #user или admin

    # Связи
    audio_files = relationship("AudioFile", back_populates="user")
    prompts = relationship("Prompt", back_populates="user")
    transcriptions = relationship("Transcription", back_populates="user")
    analysis = relationship("Analysis", back_populates="user")
    api_keys = relationship("APIKeys", back_populates="user")

    def set_password(self, password):
        
        self.password_hash = generate_password_hash(password)
       

    def check_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False