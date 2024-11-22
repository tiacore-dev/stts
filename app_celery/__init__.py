# app_celery/__init__.py

from celery import Celery
from config.config_celery import ConfigCelery


def create_celery_app(flask_app=None):
    celery = Celery(
        __name__,
        broker=ConfigCelery.CELERY_BROKER_URL,
        backend=ConfigCelery.CELERY_RESULT_BACKEND
    )
    celery.conf.update({
        'result_backend': ConfigCelery.CELERY_RESULT_BACKEND,
        'broker_connection_retry_on_startup': True
    })

    if flask_app:
        celery.conf.update(flask_app.config)
        TaskBase = celery.Task

        class ContextTask(TaskBase):
            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery.Task = ContextTask

    celery.autodiscover_tasks(['app_celery.tasks'])
    return celery
