import openai


def init_openai(app):
    openai.api_key=app.config['OPENAI_API_KEY']
    