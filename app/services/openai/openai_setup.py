import openai
import requests
import urllib3

def init_openai(app):
    # Настроим urllib3 для игнорирования SSL-сертификатов
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    
    # Создаем кастомный запрос с игнорированием SSL-сертификатов
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("https://", adapter)
    
    # Передаем кастомный session в openai
    openai.api_key = app.config['OPENAI_API_KEY']
    openai.api_base = 'https://api.openai.com/v1'
    openai.request = openai.api_requestor.APIRequestor(session=session)  # Используем custom session
    
