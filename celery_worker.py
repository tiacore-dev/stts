# celery_worker.py

from app import create_app
from app_celery import create_celery_app

print('RUNNING CELERY WORKER')

flask_app, _ = create_app()  # Создаем экземпляр Flask
celery = create_celery_app(flask_app)  # Создаем и связываем экземпляр Celery

# import ipdb
# ipdb.set_trace()

if __name__ == '__main__':
    celery.start()
