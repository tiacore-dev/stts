import openai
import openai
import ssl
import urllib3

# Отключение проверки сертификатов для всех запросов openai
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


def init_openai(app):
    openai.api_key=app.config['OPENAI_API_KEY']
    openai.api_requestor._request_class = urllib3.PoolManager(
        ssl_context=context
        )
    