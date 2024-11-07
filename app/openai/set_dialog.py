import aiohttp
import logging
import openai

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

prompt = """
Ты получаешь запись телефонного разговора. Тебе приходит три текста: весь разговор, текст первого собеседника и текст второго собеседника.
Сопоставь все эти записи и составь полноценный дилог во формате:
-Здарвствуйте.
Здравствуйте
"""

async def set_dialog(transcribed_text, channel_1, channel_2):
    logger.info("Анализ текста с помощью OpenAI.", extra={'user_id': 'openai'})

    # Формируем сообщение пользователя, проверяя, есть ли второй канал
    user_content = transcribed_text + channel_1
    if channel_2 is not None:
        user_content += channel_2

    # Формируем запрос для OpenAI
    headers = {
        'Authorization': f'Bearer {openai.api_key}',  # Замените на свой ключ API
        'Content-Type': 'application/json',
    }

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
    }

    # Выполняем асинхронный запрос с использованием aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers) as response:
            # Проверяем успешность запроса
            if response.status != 200:
                logger.error(f"Ошибка запроса к OpenAI: {response.status}", extra={'user_id': 'openai'})
                return None, 0

            # Получаем ответ
            response_data = await response.json()
            analysis = response_data['choices'][0]['message']['content']
            tokens = response_data['usage']['total_tokens']
            logger.info("Анализ текста завершен.", extra={'user_id': 'openai'})
            return analysis, tokens
