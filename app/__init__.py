from flask_jwt_extended import JWTManager
from flask import Flask
from app.api import register_namespaces
from config.config_flask import ConfigFlask
from service_registry import register_service
from app.database import init_db, set_db_globals
from app.services.s3 import init_s3_manager
from app.services.openai import init_openai
from app.utils.logger import setup_logger
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_restx import Api
from datetime import timedelta
#from app_celery import make_celery

def create_app():
    app = Flask(__name__)


    app.config.from_object(ConfigFlask)


    # Инициализация базы данных
    try:
        engine, Session, Base = init_db(app.config['SQLALCHEMY_DATABASE_URI'])
        set_db_globals(engine, Session, Base)
        from app.models import event_listeners
        logger = setup_logger()
        logger.info("База данных успешно инициализирована.", extra={'user_id': 'init'})
    except Exception as e:
        #logger.error(f"Ошибка при инициализации базы данных: {e}", extra={'user_id': 'init'})
        raise

    # Инициализация JWT
    try:
        jwt = JWTManager(app)
        register_service('jwt', jwt)
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1) 
        logger.info(f"JWT инициализирован. {app.config['JWT_ACCESS_TOKEN_EXPIRES']}", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при инициализации JWT: {e}", extra={'user_id': 'init'})
        raise

    # Инициализация OpenAI
    try:
        init_openai(app)
        register_service('openai', init_openai)
        logger.info("OpenAI успешно инициализирован.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при инициализации OpenAI: {e}", extra={'user_id': 'init'})
        raise

    # Инициализация S3
    try:
        s3_manager = init_s3_manager(app)
        register_service('s3_manager', s3_manager)
        logger.info("S3 менеджер успешно инициализирован.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при инициализации S3: {e}", extra={'user_id': 'init'})
        raise

    
    # Инициализация SocketIO
    socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")
    register_service('socketio', socketio)

    # Проверьте, что socketio зарегистрирован
    if socketio is None:
        raise RuntimeError("SocketIO не был правильно инициализирован!")



    from app.routes import register_routes
    # Регистрация маршрутов
    try:
        register_routes(app)
        logger.info("Маршруты успешно зарегистрированы.", extra={'user_id': 'init'})
    except Exception as e:
        logger.error(f"Ошибка при регистрации маршрутов: {e}", extra={'user_id': 'init'})
        raise

    # Инициализация API
    api = Api(app, doc='/swagger', security='apiKey', authorizations={
        'apiKey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'API-Key',
            'description': 'Добавьте API-ключ в заголовок `Authorization``'
            }})
    
     # Регистрация маршрутов
    register_namespaces(api)


    # Настройка CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    #celery = make_celery(app)
    #app.celery = celery

    return app, socketio
