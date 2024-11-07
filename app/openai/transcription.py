import openai
import aiohttp
import asyncio
from io import BytesIO
import logging

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

# Класс BytesIO с именем
class NamedBytesIO(BytesIO):
    def __init__(self, initial_bytes, name):
        super().__init__(initial_bytes)
        self.name = name

# Асинхронная транскрибация аудио
async def transcribe_audio(audio, file_format):
    logger.info("Начало транскрибации аудио.", extra={'user_id': 'openai'})
    audio_file = NamedBytesIO(audio, f"audio.{file_format}")
    audio_file.seek(0)

    try:
        logger.info("Отправка аудио на транскрибацию.", extra={'user_id': 'openai'})

        # Создаем асинхронный HTTP запрос с использованием aiohttp
        async with aiohttp.ClientSession() as session:
            url = "https://api.openai.com/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {openai.api_key}"
                # Убрали Content-Type, чтобы он был автоматически установлен
            }

            # Подготовка данных для отправки
            data = aiohttp.FormData()
            data.add_field("model", "whisper-1")
            data.add_field("language", "ru")
            data.add_field("file", audio_file, filename=f"audio.{file_format}")

            # Отправка запроса
            async with session.post(url, headers=headers, data=data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    transcribed_text = response_data['text']
                    logger.info(f"Транскрибация завершена, текст: {transcribed_text}.", extra={'user_id': 'openai'})
                    return transcribed_text
                else:
                    logger.error(f"Ошибка при транскрибации аудио: {response_data}", extra={'user_id': 'openai'})
                    raise Exception(f"Error: {response_data}")
    except Exception as e:
        logger.error(f"Ошибка при транскрибации аудио: {e}", extra={'user_id': 'openai'})
        raise
    finally:
        audio_file.close()
        logger.info("Закрытие объекта BytesIO.", extra={'user_id': 'openai'})
