from app.openai.analyze_text import analyze_text
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from app.utils.db_get import get_prompt, get_transcription

logger = logging.getLogger('chatbot')

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analysis/create', methods=['POST'])
@jwt_required()
def create_analysis():
    from app.database.managers.analysis_manager import AnalysisManager
    db = AnalysisManager()
    data = request.json
    prompt_id = data['prompt_id']
    transcription_id = data['transcription_id']
    current_user = get_jwt_identity()
    prompt=get_prompt(prompt_id)
    transcription = get_transcription(transcription_id)
    text, tokens = analyze_text(prompt, transcription)
    analysis_id = db.add_analysis(text, current_user['user_id'], prompt_id, transcription_id, tokens)
    return jsonify({"analysis_id": analysis_id}), 200


@analysis_bp.route('/analysis/get_all', methods=['GET'])
@jwt_required()
def get_analysis():
    from app.database.managers.analysis_manager import AnalysisManager
    db = AnalysisManager()
    current_user = get_jwt_identity()
    offset = request.args.get('offset', default=0, type=int)  # Получаем offset из параметров запроса
    limit = request.args.get('limit', default=10, type=int)  # Получаем limit из параметров запроса
    logger.info(f"Запрос транскрипций для пользователя: {current_user['user_id']} с offset={offset} и limit={limit}", extra={'user_id': current_user['login']})
    analysis = db.get_analysis_by_user(current_user['user_id'], offset, limit)
    
    if analysis:
        logger.info("Транскрипции найдены.", extra={'user_id': current_user['login']})
        return jsonify(analysis), 200
    else:
        logger.warning("Транскрипции не найдены.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "No analysiss found"}), 404
    

@analysis_bp.route('/analysis/<analysis_id>/view', methods=['GET'])
@jwt_required()
def get_analysis_by_analysis_id(analysis_id):
    current_user = get_jwt_identity()
    logger.info(f"Запрос на получение анализа по analysis_id: {analysis_id} для пользователя: {current_user}", extra={'user_id': current_user['login']})
    from app.database.managers.analysis_manager import AnalysisManager
    
    db =AnalysisManager()

    analysis = db.get_analysis_by_id(analysis_id)

    if analysis:
        return jsonify(analysis), 200
    else:
        logger.warning("Анализ не найден.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "analysis not found"}), 404