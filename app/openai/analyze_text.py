import aiohttp
import logging
import openai

# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

async def analyze_text(prompt, transcribed_text):
    logger.info("Анализ текста с помощью OpenAI.", extra={'user_id': 'openai'})

    # Формируем данные для запроса
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"  # Замените на ваш API-ключ
    }

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcribed_text}
        ]
    }

    # Создаем асинхронный запрос с помощью aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()  # Получаем ответ в формате JSON
                analysis = result['choices'][0]['message']['content']
                tokens = result['usage']['total_tokens']
                logger.info("Анализ текста завершен.", extra={'user_id': 'openai'})
                return analysis, tokens
            else:
                logger.error(f"Ошибка при анализе текста: {response.status}", extra={'user_id': 'openai'})
                return None, 0
