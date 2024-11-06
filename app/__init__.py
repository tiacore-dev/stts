from flask import Flask
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import init_db, set_db_globals
from app.s3 import init_s3_manager
from admin import admin
from app.routes import register_routes
from app.openai import init_openai
from app.utils.logger import setup_logger   # Импортируем логгер

load_dotenv()

from functools import wraps
from flask import g  



def create_app():
    app = Flask(__name__)
    
    # Настройки приложения
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        #logger.info("Настройки приложения загружены.")
    except Exception as e:
        #logger.error(f"Ошибка при загрузке настроек приложения: {e}")
        raise

    # Инициализация базы данных
    try:
        engine, Session, Base = init_db(app)
        set_db_globals(engine, Session, Base)
        #admin('admin', 'admin', 'admin')
        logger=setup_logger()
        logger.info("База данных успешно инициализирована.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}", extra={'user_id': 'init'})
        raise

    # Настройка JWT
    try:
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Секретный ключ для JWT
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # Время истечения токена доступа
        jwt = JWTManager(app)
        logger.info("JWT инициализирован.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при инициализации JWT: {e}", extra={'user_id': 'init'})
        raise

    # Настройка OpenAI
    try:
        app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
        logger.info("Настройки OpenAI загружены.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при загрузке настроек OpenAI: {e}", extra={'user_id': 'init'})
        raise
    
    # Настройка хранилища s3
    try:
        app.config['endpoint_url']=os.getenv('ENDPOINT_URL')
        app.config['region_name']=os.getenv('REGION_NAME')
        app.config['aws_access_key_id']=os.getenv('AWS_ACCESS_KEY_ID')
        app.config['aws_secret_access_key']=os.getenv('AWS_SECRET_ACCESS_KEY')
        app.config['bucket_name']=os.getenv('BUCKET_NAME')
        logger.info("Настройки s3 хранилища загружены.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при загрузке настроек s3 хранилища: {e}", extra={'user_id': 'init'})
        raise




    

    # Инициализация OpenAI
    try:
        init_openai(app)
        logger.info("OpenAI успешно инициализирован.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при инициализации OpenAI: {e}", extra={'user_id': 'init'})
        raise

    # Инициализация s3
    try:
        init_s3_manager(app)
        logger.info("s3 хранилище успешно инициализировано.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при инициализации s3 хранилища: {e}", extra={'user_id': 'init'})
        raise

    # Регистрация маршрутов
    try:
        register_routes(app)
        logger.info("Маршруты успешно зарегистрированы.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при регистрации маршрутов: {e}", extra={'user_id': 'init'})
        raise


    

    return app