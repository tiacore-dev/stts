from flask_restx import fields, Model


transcription_create_model_payload = Model('TranscriptionCreatePayload', {
    'audio_url': fields.String(required=True, description='URL с аудиозаписью'),
    'channels': fields.Integer(required=False, description='Количество каналов'),
    'new_filename': fields.String(required=False, description='Новое имя для аудофайла, если необходимо'),
    'prompt': fields.String(required=False, description='Промпт для оставления диалога'),
})

transcription_create_model_response = Model('TranscriptionCreateResponse', {
    'transcription_id': fields.String(required=True, description='ID получившейся транскрипции'),
    'task_id': fields.String(required=True, description='Текст получившейся транскрипции'),
})

transcription_model = Model('Transcription', {
    'transcription_id': fields.String(required=True, description='ID  транскрипции'),
    'text': fields.String(required=True, description='Текст транскрипции'),
    'audio_file_name': fields.String(required=True, description='Название аудиозаписи')
})