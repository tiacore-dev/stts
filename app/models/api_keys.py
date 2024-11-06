from app.database.db_setup import Base 
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class APIKeys(Base):
    __tablename__ = 'api_keys'

    api_key = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)  # Внешний ключ
    comment = Column(Text)

    # Связи
    user = relationship("User", back_populates="api_keys")