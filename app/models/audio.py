from app.database.db_setup import Base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
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

    # Связи
    user = relationship("User", back_populates="audio_files")