# app_celery/__init__.py

from celery import Celery
from config.config_celery import ConfigCelery
from service_registry import register_service

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
    #celery.autodiscover_tasks(['app.app_celery.tasks'])
    register_service('celery', celery)
    # Явный импорт задач
    from app.app_celery.tasks.transcription_tasks import process_and_transcribe_audio_task, process_and_upload_file_task

    # Явная регистрация задач
    celery.conf.update(
        task_routes={
            'app.app_celery.tasks.transcription_tasks.process_and_transcribe_audio_task': {'queue': 'celery'},
            'app.app_celery.tasks.transcription_tasks.process_and_upload_file_task': {'queue': 'celery'},
        }
    )
    return celery
