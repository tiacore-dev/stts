import openai
import ssl
import urllib3

def init_openai(app):
    # Создаем PoolManager с отключенной проверкой SSL-сертификатов
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    
    # Настроим openai для использования кастомного HTTP-клиента
    openai.api_key = app.config['OPENAI_API_KEY']
    openai.api_base = "https://api.openai.com/v1"

    # Устанавливаем кастомный http клиент
    openai.http = http

