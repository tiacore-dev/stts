# celery_worker.py

from app import create_app
from app.app_celery import create_celery_app
from service_registry import get_service
flask_app, _ = create_app()  # Создаем экземпляр Flask
#celery = create_celery_app(flask_app)  # Создаем и связываем экземпляр Celery
celery = get_service('celery')

if __name__ == '__main__':
    celery.start()
