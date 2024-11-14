from app.database.db_setup import Base 
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class APIKeys(Base):
    __tablename__ = 'api_keys'

    key_id = Column(String, primary_key=True)
    api_key = Column(String, nullable=False)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)  # Внешний ключ
    comment = Column(Text)

    # Связи
    user = relationship("User", back_populates="api_keys")

    def to_dict(self):
        """Преобразование объекта в словарь."""
        return {
            "key_id": self.key_id,
            "user_id": self.user_id,
            "comment": self.comment
        }