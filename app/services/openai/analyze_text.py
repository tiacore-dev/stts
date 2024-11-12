import openai# Импортируем логгер
import logging
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')


def analyze_text(prompt, transcribed_text):
    logger.info("Анализ текста с помощью OpenAI.", extra={'user_id': 'openai'})
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": transcribed_text}]
    )
    analysis = response.choices[0].message.content
    tokens = response.usage.total_tokens
    logger.info("Анализ текста завершен.", extra={'user_id': 'openai'})
    return analysis, tokens