# app_celery/__init__.py

from celery import Celery
from config.config_celery import ConfigCelery

def create_celery_app(flask_app=None):
    # Создаем экземпляр Celery
    celery = Celery(
        __name__,
        broker=ConfigCelery.CELERY_BROKER_URL,
        backend=ConfigCelery.CELERY_RESULT_BACKEND
    )
    celery.conf.update(result_backend=ConfigCelery.CELERY_RESULT_BACKEND)

    # Если передан flask_app, связываем конфигурации
    if flask_app:
        celery.conf.update(flask_app.config)
        # Устанавливаем контекст приложения, чтобы задачи могли его использовать
        TaskBase = celery.Task

        class ContextTask(TaskBase):
            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery.Task = ContextTask

    # Автоматически обнаруживает задачи в модуле 'app_celery.tasks'
    celery.autodiscover_tasks(['app_celery.tasks'])
    return celery
