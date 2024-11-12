import os
from dotenv import load_dotenv

load_dotenv()

class ConfigCelery:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Используем Redis для Celery
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'