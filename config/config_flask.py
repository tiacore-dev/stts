import os
from dotenv import load_dotenv

load_dotenv()

class ConfigFlask:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ENDPOINT_URL = os.getenv('ENDPOINT_URL')
    REGION_NAME = os.getenv('REGION_NAME')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    CORS_ORIGINS = os.getenv('ORIGIN', '*')