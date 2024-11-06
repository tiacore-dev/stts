from sqlalchemy import exists
from app.models.user import User  
from app.database.db_globals import Session
import uuid

class UserManager:
    def __init__(self):
        self.Session = Session

    def add_user(self, username, login, password, user_type='user'):
        """Добавляем пользователя стандартно"""
        session = self.Session()
        user_id = uuid.uuid4()
        new_user = User(user_id=user_id, username=username, login=login,  user_type=user_type)
        new_user.set_password(password)  # Устанавливаем хэш пароля
        session.add(new_user)
        session.commit()
        session.close()
        return user_id

    def check_password(self, username, password):
        """Проверяем пароль пользователя"""
        session = self.Session()
        user = session.query(User).filter_by(login=username).first()
        session.close()
        if user and user.check_password(password):
            return True
        return False

    def update_user_password(self, username, new_password):
        """Обновляем пароль пользователя"""
        session = self.Session()
        user = session.query(User).filter_by(login=username).first()
        if user:
            user.set_password(new_password)  # Обновляем хэш пароля
            session.commit()
        session.close()


    def user_exists(self, user_id):
        """Проверка существования пользователя по имени"""
        session = self.Session()
        exists_query = session.query(exists().where(User.login == user_id)).scalar()
        session.close()
        return exists_query
    
    
    def get_user_by_user_id(self, user_id):
        session = self.Session()
        try:
            # Получаем пользователя по id
            user = session.query(User).filter_by(user_id=user_id).first()
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата запроса
            session.close()

        # Возвращаем найденного пользователя или None, если не найдено
        return user
    
    def is_user_admin(self, user_id):
        """Проверка является ли пользователь admin"""
        session = self.Session()
        try:
            # Получаем пользователя по id
            user = session.query(User).filter_by(user_id=user_id).first()
            if user.user_type == 'admin':
                return True
            else: 
                return False
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата запроса
            session.close()

    def get_user_id(self, user_id):
        session = self.Session()
        try:
            # Получаем пользователя по id
            user = session.query(User).filter_by(login=user_id).first()
            return user.user_id
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата запроса
            session.close()
        