from app.services.openai.analyze_text import analyze_text
from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from app.utils.db_get import get_prompt, get_transcription
from app.utils.db_get import get_audio_name, get_prompt_name

logger = logging.getLogger('chatbot')

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis', methods=['GET'])
def transcription():
    return render_template('analysis/analysis.html')



@analysis_bp.route('/analysis_result', methods=['GET'])
def analysis_result():
    return render_template('analysis/analysis_result.html')


@analysis_bp.route('/analysis/create', methods=['POST'])
@jwt_required()
def create_analysis():
    from app.database.managers.analysis_manager import AnalysisManager
    db = AnalysisManager()
    data = request.json
    prompt_id = data['prompt_id']
    transcription_ids = data['transcription_ids']  # Получаем список transcription_id
    current_user = get_jwt_identity()
    logger.info(f"Запрос анализа транскрибаций с ID {transcription_ids} и промптом с ID: {prompt_id}.", extra={'user_id': current_user['login']})
    
    # Получаем prompt для анализа
    prompt = get_prompt(prompt_id)
    
    # Создаем задачи анализа текста для каждого transcription_id
    analysis = []
    for transcription_id in transcription_ids:
        transcription = get_transcription(transcription_id)  # Получаем транскрипцию
        analysis.append(analyze_text(prompt, transcription))  # Добавляем задачу анализа текста

    logger.info(f"Начат анализ транскрибаций.", extra={'user_id': current_user['login']})
    
    # Выполняем все задачи параллельно
    try:
        # Обрабатываем результаты анализа и сохраняем только успешные
        analysis_ids = []
        for transcription_id, result in zip(transcription_ids, analysis):
            if not isinstance(result, Exception):
                text, tokens = result
                analysis_id = db.add_analysis(text, current_user['user_id'], prompt_id, transcription_id, tokens)
                analysis_ids.append({"transcription_id": transcription_id, "analysis_id": analysis_id})
            else:
                logger.error(f"Ошибка в процессе анализа для transcription_id {transcription_id}: {result}")
        logger.info(f"Анализ завершен.", extra={'user_id': current_user['login']})
        return jsonify({"analyses": analysis_ids}), 200
    except Exception as e:
        logger.error(f"Ошибка в процессе параллельного анализа: {e}")
        return jsonify({'msg': 'Error processing analysis.'}), 500



@analysis_bp.route('/analysis/all', methods=['GET'])
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
    

@analysis_bp.route('/api/analysis/<analysis_id>', methods=['GET'])
@jwt_required()
def get_transcription_by_id(analysis_id):
    current_user = get_jwt_identity()
    logger.info(f"Запрос на получение транскрипции по analysis_id: {analysis_id} для пользователя: {current_user}", extra={'user_id': current_user})
    from app.database.managers.analysis_manager import AnalysisManager
    
    db = AnalysisManager()
    analysis = db.get_analysis_by_id(analysis_id)

    if transcription:
        return jsonify({
            "text": analysis['text'],
            "tokens": transcription['tokens'],
            "audio_file_name": get_audio_name(analysis['audio_id']),
            "prompt_name": get_prompt_name(analysis['prompt_id'])
        }), 200
    else:
        logger.warning("Анализ не найдена.", extra={'user_id': current_user['login']})
        return jsonify({"msg": "analysis not found"}), 404

@analysis_bp.route('/analysis/<analysis_id>/view', methods=['GET'])
@jwt_required()
def get_analysis_by_analysis_id(analysis_id):
    current_user = get_jwt_identity()
    logger.info(f"Запрос на отображение транскрипции с analysis_id: {analysis_id} для пользователя: {current_user}", extra={'user_id': current_user['login']})
    
    # Передаем только transcription_id в шаблон
    return render_template('analysis/analysis_details.html', analysis_id=analysis_id)
    

@analysis_bp.route('/user_prompts', methods=['GET'])
@jwt_required()
def get_user_prompts():
    from app.database.managers.prompt_manager import PromptManager
    prompt_manager = PromptManager()
    current_user = get_jwt_identity()
    logger.info(f"Запрос готовых промптов для пользователя: {current_user}", extra={'user_id': current_user['login']})
    prompts = prompt_manager.get_prompts_by_user(current_user['user_id'])  # Извлекаем промпты для текущего пользователя
    prompt_data = []
    for s in prompts:
        prompt_info = {
            "prompt_name": s[0],
            "prompt_id": s[2]
        }
        prompt_data.append(prompt_info)
    if prompt_data:
        return jsonify(prompt_data=prompt_data), 200
    else:
        return jsonify({"msg": "No prompts found"}), 404
    

@analysis_bp.route('/user_transcriptions', methods=['GET'])
@jwt_required()
def get_user_transcriptions():
    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()
    current_user = get_jwt_identity()
    
    logger.info(f"Запрос готовых промптов для пользователя: {current_user}", extra={'user_id': current_user['login']})
    transcriptions = db.get_transcription_by_user(current_user['user_id'])  # Извлекаем промпты для текущего пользователя
    names = [{
        "transcription_id": t['transcription_id'],
        "audio_name": get_audio_name(t['audio_id'])
    } for t in transcriptions]

    if names:
        return jsonify(transcription=names), 200
    else:
        return jsonify({"msg": "No prompts found"}), 404
