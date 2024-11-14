import aiohttp
import logging
import openai
from .prompt import default_prompt
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')



async def set_dialog(transcribed_text, channel_1, channel_2, custom_prompt):
    logger.info("Анализ текста с помощью OpenAI.", extra={'user_id': 'openai'})

    # Формируем сообщение пользователя, проверяя, есть ли второй канал
    user_content = transcribed_text + channel_1
    if channel_2 is not None:
        user_content += channel_2

    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = default_prompt

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
