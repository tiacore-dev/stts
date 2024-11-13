import openai
from io import BytesIO
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


# Класс BytesIO с именем
class NamedBytesIO(BytesIO):
    def __init__(self, initial_bytes, name):
        super().__init__(initial_bytes)
        self.name = name

# Транскрибация аудио
def transcribe_audio(audio, file_format):
    logger.info("Начало транскрибации аудио.", extra={'user_id': 'openai'})
    audio_file = NamedBytesIO(audio, f"audio.{file_format}")
    audio_file.seek(0)

    try:
        logger.info("Отправка аудио на транскрибацию.", extra={'user_id': 'openai'})
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ru"
        )
        transcribed_text = response.text
        logger.info("Транскрибация завершена.", extra={'user_id': 'openai'})
        return transcribed_text
    except Exception as e:
        logger.error(f"Ошибка при транскрибации аудио: {e}", extra={'user_id': 'openai'})
        raise
    finally:
        audio_file.close()
        logger.info("Закрытие объекта BytesIO.", extra={'user_id': 'openai'})