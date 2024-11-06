from app.database.db_setup import Base 
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Prompt(Base):
    __tablename__ = 'prompts'

    prompt_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)  # Внешний ключ
    prompt_name = Column(String(255), nullable=False)  # Название промпта
    text = Column(Text)  # Текст промпта
    use_automatic = Column(Boolean, nullable=True, default=False)  # Новый булевый столбец

    # Связи
    user = relationship("User", back_populates="prompts")

    def to_dict(self):
        return {
            "prompt_id": self.prompt_id,
            "user_id": self.user_id,
            "prompt_name": self.prompt_name,
            "text": self.text,
            "use_automatic": self.use_automatic # Форматируем дату для JSON
        }
