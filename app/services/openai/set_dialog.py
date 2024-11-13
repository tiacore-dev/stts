import aiohttp
import logging
import openai

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

prompt = """
Ты получаешь запись телефонного разговора. Тебе приходит три текста: весь разговор, текст первого собеседника и текст второго собеседника.
Сопоставь все эти записи и составь полноценный дилог во формате:
-Здарвствуйте.
-Здравствуйте.
"""

async def set_dialog(transcribed_text, channel_1, channel_2):
    logger.info("Анализ текста с помощью OpenAI.", extra={'user_id': 'openai'})

    # Формируем сообщение пользователя, проверяя, есть ли второй канал
    user_content = transcribed_text + channel_1
    if channel_2 is not None:
        user_content += channel_2

    # Отправляем запрос в OpenAI
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
    )
    
    analysis = response.choices[0].message.content
    tokens = response.usage.total_tokens
    logger.info("Анализ текста завершен.", extra={'user_id': 'openai'})
    return analysis, tokens
