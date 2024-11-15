import openai
import openai
import ssl
import urllib3

"""# Отключение проверки сертификатов для всех запросов openai
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE"""


def init_openai(app):
    # Настроим urllib3 для игнорирования SSL-сертификатов
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    
    # Обновляем настройки openai для использования custom HTTP-клиента
    openai.api_base = 'https://api.openai.com/v1'
    openai.api_key = app.config['OPENAI_API_KEY']
    
    # Используем кастомный HTTP-клиент для всех запросов
    openai.request = openai.api_requestor.APIRequestor(http)
    