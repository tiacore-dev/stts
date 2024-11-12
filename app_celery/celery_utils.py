from celery import Celery
import os

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=os.getenv('CELERY_BROKER_URL'),
        backend=os.getenv('CELERY_RESULT_BACKEND')
    )
    celery.conf.update(app.config)

    # Делаем Flask-контекст доступным для задач
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
