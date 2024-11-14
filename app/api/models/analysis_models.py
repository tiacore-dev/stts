from flask_restx import fields, Model


analysis_create_model_payload = Model('AnalysisCreatePayload', {
    'transcription_id': fields.String(required=True, description='ID транскрипции для анализа'),
    'prompt': fields.String(required=False, description='Собственный промпт для анализа'),
    'prompt_id': fields.Integer(required=False, description='ID промпта, существующего в базе данных')
})

analysis_create_model_response = Model('AnalysisCreateResponse', {
    'analysis_id': fields.String(required=True, description='ID получившегося анализа'),
    'analysis_text': fields.String(required=True, description='Текст получившегося анализа'),
})

analysis_model = Model('Analysis', {
    'analysis_id': fields.String(required=True, description='ID анализа'),
    'text': fields.String(required=True, description='Текст анализа'),
    'prompt': fields.String(required=True, description='Использовавшийся промпт'),
    'transcription': fields.String(required=True, description='Использовавшаяся транскрипция'),
    'tokens': fields.String(required=True, description='Количество потраченных токенов')
})