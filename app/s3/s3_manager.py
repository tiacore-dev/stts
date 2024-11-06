import aioboto3
from botocore.config import Config
import logging
import asyncio

# Получаем логгер
logger = logging.getLogger('chatbot')

class S3Manager:
    def __init__(self, app):
        app.logger.info("Инициализация асинхронного S3 клиента.")
        self.session = aioboto3.Session()
        self.endpoint_url = app.config['endpoint_url']
        self.region_name = app.config['region_name']
        self.aws_access_key_id = app.config['aws_access_key_id']
        self.aws_secret_access_key = app.config['aws_secret_access_key']

    async def get_client(self):
        return self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            config=Config(s3={'addressing_style': 'path'})
        )

    async def upload_fileobj(self, file_obj, bucket_name, object_name):
        """Загружает файл напрямую из объекта файла в S3 асинхронно."""
        async with await self.get_client() as s3_client:
            logger.info(f"Загрузка файла в bucket '{bucket_name}' с именем '{object_name}'.", extra={'user_id': 's3'})
            try:
                await s3_client.upload_fileobj(file_obj, bucket_name, object_name)
                logger.info(f"Файл успешно загружен в {bucket_name}/{object_name}.", extra={'user_id': 's3'})
            except Exception as e:
                logger.error(f"Ошибка при загрузке файла: {e}", extra={'user_id': 's3'})

    async def download_file(self, bucket_name, object_name):
        """Асинхронно скачивает файл из S3 и возвращает его содержимое."""
        async with await self.get_client() as s3_client:
            logger.info(f"Скачивание файла '{object_name}' из bucket '{bucket_name}'.", extra={'user_id': 's3'})
            try:
                response = await s3_client.get_object(Bucket=bucket_name, Key=object_name)
                file_content = await response['Body'].read()
                logger.info(f"Файл '{object_name}' успешно скачан.", extra={'user_id': 's3'})
                return file_content
            except Exception as e:
                logger.error(f"Ошибка при скачивании файла '{object_name}': {e}", extra={'user_id': 's3'})
                return None

    async def list_files(self, bucket_name, prefix=""):
        """Асинхронно получает список файлов в указанном bucket."""
        async with await self.get_client() as s3_client:
            logger.info(f"Получение списка файлов из bucket '{bucket_name}' с префиксом '{prefix}'.", extra={'user_id': 's3'})
            try:
                response = await s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
                files = [obj['Key'] for obj in response.get('Contents', [])]
                logger.info(f"Найдено {len(files)} файлов.", extra={'user_id': 's3'})
                return files
            except Exception as e:
                logger.error(f"Ошибка при получении списка файлов из bucket '{bucket_name}': {e}", extra={'user_id': 's3'})
                return []

    async def delete_file(self, bucket_name, object_name):
        """Асинхронно удаляет файл из S3."""
        async with await self.get_client() as s3_client:
            logger.info(f"Удаление файла '{object_name}' из bucket '{bucket_name}'.", extra={'user_id': 's3'})
            try:
                await s3_client.delete_object(Bucket=bucket_name, Key=object_name)
                logger.info(f"Файл '{object_name}' успешно удален из bucket '{bucket_name}'.", extra={'user_id': 's3'})
            except Exception as e:
                logger.error(f"Ошибка при удалении файла '{object_name}': {e}", extra={'user_id': 's3'})

    # Другие методы, такие как generate_presigned_url, file_exists и get_file_metadata, можно также реализовать асинхронно, аналогично вышеуказанным методам
    async def generate_presigned_url(self, bucket_name, object_name, expiration=3600):
        async with await self.get_client() as s3_client:
            logger.info(f"Генерация временного URL для файла '{object_name}' в bucket '{bucket_name}', срок действия {expiration} секунд.", extra={'user_id': 's3'})
            try:
                response = await s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': object_name},
                    ExpiresIn=expiration
                )
                logger.info(f"URL успешно сгенерирован для файла '{object_name}'.", extra={'user_id': 's3'})
                return response
            except Exception as e:
                logger.error(f"Ошибка при генерации URL для файла '{object_name}': {e}", extra={'user_id': 's3'})
                return None

    async def file_exists(self, bucket_name, object_name):
        async with await self.get_client() as s3_client:
            logger.info(f"Проверка существования файла '{object_name}' в bucket '{bucket_name}'.", extra={'user_id': 's3'})
            try:
                await s3_client.head_object(Bucket=bucket_name, Key=object_name)
                logger.info(f"Файл '{object_name}' существует в bucket '{bucket_name}'.", extra={'user_id': 's3'})
                return True
            except Exception as e:
                logger.warning(f"Файл '{object_name}' не найден в bucket '{bucket_name}': {e}", extra={'user_id': 's3'})
                return False

    async def get_file_metadata(self, bucket_name, object_name):
        async with await self.get_client() as s3_client:
            logger.info(f"Получение метаданных для файла '{object_name}' из bucket '{bucket_name}'.", extra={'user_id': 's3'})
            try:
                response = await s3_client.head_object(Bucket=bucket_name, Key=object_name)
                logger.info(f"Метаданные для файла '{object_name}' получены.", extra={'user_id': 's3'})
                return {
                    'ContentType': response['ContentType'],
                    'ContentLength': response['ContentLength'],
                    'LastModified': response['LastModified'],
                }
            except Exception as e:
                logger.error(f"Ошибка при получении метаданных для файла '{object_name}': {e}", extra={'user_id': 's3'})
                return None

    async def get_file(self, bucket_name, object_name):
        async with await self.get_client() as s3_client:
            logger.info(f"Получение файла '{object_name}' из bucket '{bucket_name}'.", extra={'user_id': 's3'})
            try:
                response = await s3_client.get_object(Bucket=bucket_name, Key=object_name)
                file_content = response['Body'].read()  # Чтение содержимого файла в байты
                logger.info(f"Файл '{object_name}' успешно получен.", extra={'user_id': 's3'})
                return file_content
            except Exception as e:
                logger.error(f"Ошибка при получении файла '{object_name}': {e}", extra={'user_id': 's3'})
                return None