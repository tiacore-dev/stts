from app.database.db_setup import Base
from sqlalchemy import Column, String,  Float, DateTime, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class AudioFile(Base):
    __tablename__ = 'audio_files'

    audio_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)  # Внешний ключ
    file_name = Column(String(255), nullable=False)  # Название файла
    file_extension = Column(String(255), nullable=False)
    file_size = Column(Float, nullable=False)  # Размер файла в байтах
    upload_date = Column(DateTime, default=datetime.utcnow)  # Дата загрузки файла
    bucket_name = Column(String(255), nullable=False)  # Имя S3 bucket
    s3_key = Column(String(255), nullable=False)  # Путь к файлу в S3
    transcribed = Column(Boolean)
    

    # Связи
    user = relationship("User", back_populates="audio_files")

    def to_dict(self):
        return {
            "audio_id": self.audio_id,
            "user_id": self.user_id,
            "file_name": self.file_name,
            "file_extension": self.file_extension,
            "file_size": self.file_size, # Форматируем дату для JSON
            "upload_date": self.upload_date,
            "bucket_name": self.bucket_name,
            "s3_key": self.s3_key,
            "transcribed": self.transcribed
        }