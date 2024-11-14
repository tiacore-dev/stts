from app.utils.db_get import get_audio_name, get_prompt_name
from flask import request, jsonify, current_app
from app.utils.db_get import get_prompt, get_transcription
import logging
from app.services.openai.analyze_text import analyze_text
from flask_restx import Namespace, Resource
from app.decorators import api_key_required
from app.api.models import analysis_create_model_payload, analysis_create_model_response, analysis_model
# Получаем логгер по его имени
logger = logging.getLogger('chatbot')

analysis_ns = Namespace('api/analysis', description='Schedule Details operations')

analysis_ns.models[analysis_create_model_payload.name] = analysis_create_model_payload
analysis_ns.models[analysis_create_model_response.name] = analysis_create_model_response
analysis_ns.models[analysis_model.name] = analysis_model

@analysis_ns.route('/create')
class AnalysisResource(Resource):
    @api_key_required
    @analysis_ns.expect(analysis_create_model_payload)
    @analysis_ns.marshal_with(analysis_create_model_response)
    def post(self):
        from app.database.managers.analysis_manager import AnalysisManager
        db = AnalysisManager()
        data = request.json
        prompt_id = data.get('prompt_id', None)
        custom_prompt=data.get('prompt', None)
        transcription_id = data['transcription_id']  # Получаем  transcription_id
        user_id = request.user_id
        logger.info(f"Запрос анализа транскрибаций с ID {transcription_id} и промптом с ID: {prompt_id}.", extra={'user_id': user_id})
        # Получаем prompt для анализа
        if prompt_id:
            prompt = get_prompt(prompt_id)
        if custom_prompt:
            prompt=custom_prompt
            from app.database.managers.prompt_manager import PromptManager
            db_p=PromptManager()
            prompt_id = db_p.add_prompt(user_id, 'custom_prompt', prompt)
        transcription = get_transcription(transcription_id)  # Получаем транскрипцию
        logger.info(f"Начат анализ транскрибаций.", extra={'user_id': user_id})
        analysis, tokens=analyze_text(prompt, transcription)  # Добавляем задачу анализа текста
        # Выполняем все задачи параллельно
        try:
            analysis_id = db.add_analysis(analysis, user_id, prompt_id, transcription_id, tokens)
            logger.info(f"Анализ завершен.", extra={'user_id': user_id})
            return jsonify({"analysis_id": analysis_id, "analysis_text": analysis}), 200
        except Exception as e:
            logger.error(f"Ошибка в процессе параллельного анализа: {e}")
            return jsonify({'msg': 'Error processing analysis.'}), 500
    
@analysis_ns.route('/<analysis_id>')
class AnalysisResource(Resource):
    @api_key_required
    @analysis_ns.marshal_with(analysis_model)
    def get(self, analysis_id):
        # Получаем user_id, который был добавлен в декораторе
        user_id = request.user_id
        logger.info(f"Запрос на получение транскрипции по transcription_id: {analysis_id} для пользователя: {user_id}", extra={'user_id': user_id})
        from app.database.managers.analysis_manager import AnalysisManager
        db = AnalysisManager()
        analysis = db.get_analysis_by_id(analysis_id)
        prompt = get_prompt(analysis.prompt_id)
        transcription = get_transcription( analysis.transcription_id) 
        if analysis:
            return jsonify({ 
                'analysis_id': analysis_id,
                'text': analysis.text,
                'prompt': prompt,
                'transcription': transcription,
                'tokens': analysis.tokens
            }), 200
        else:
            logger.warning("Анализ не найден.", extra={'user_id': user_id})
            return jsonify({"msg": "Analysis not found"}), 404
        
@analysis_ns.route('/all')
class AnalysisResource(Resource):
    @api_key_required
    @analysis_ns.marshal_list_with(analysis_model)
    def get(self):
        from app.database.managers.analysis_manager import AnalysisManager
        db = AnalysisManager()
        user_id = request.user_id
        offset = request.args.get('offset', default=0, type=int)  # Получаем offset из параметров запроса
        limit = request.args.get('limit', default=0, type=int)  # Получаем limit из параметров запроса
        logger.info(f"Запрос транскрипций для пользователя: {user_id} с offset={offset} и limit={limit}", extra={'user_id': user_id})
        analysis = db.get_analysis_by_user(user_id, offset, limit)
        analysis_data=[]
        for a in analysis:
            prompt = get_prompt(a['prompt_id'])
            transcription = get_transcription(a['transcription_id'])
            analysis_data.append({
                'analysis_id': a['analysis_id'],
                'text': a['text'],
                'prompt': prompt,
                'transcription': transcription,
                'tokens': a['tokens']
            })

        if analysis_data:
            logger.info("Транскрипции найдены.", extra={'user_id': user_id})
            return jsonify(analysis), 200
        else:
            logger.warning("Транскрипции не найдены.", extra={'user_id': user_id})
            return jsonify({"msg": "No analysiss found"}), 404