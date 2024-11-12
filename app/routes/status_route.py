from flask import Blueprint, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.celery_task import CeleryTask 
import logging
from app_celery.tasks.transcription_tasks import process_and_transcribe_audio_task

logger = logging.getLogger('chatbot')


status_bp = Blueprint('status', __name__)

@status_bp.route('/status', methods=['GET'])
def status_page():
    return render_template('status.html')


@status_bp.route('/api/tasks/statuses', methods=['GET'])
@jwt_required()
def get_task_statuses():
    # Получаем текущего пользователя
    current_user = get_jwt_identity()
    
    # Получаем список задач пользователя (должно быть реализовано)
    user_tasks = get_user_tasks(current_user['user_id'])  # Например, эта функция возвращает задачи для пользователя
    
    statuses = []
    for task in user_tasks:
        task_status = CeleryTask.get_status(task.task_id)
        statuses.append({
            "task_name": task.name,
            "status": task_status['status'],
            "message": task_status.get('message', '')
        })

    return jsonify({"tasks": statuses}), 200



from celery.result import AsyncResult

def get_user_tasks(user_id):
    # Используем AsyncResult для получения статуса задачи по task_id
    task_ids = []  # Здесь ваш код для получения task_id для пользователя (например, из базы данных)
    
    tasks = []
    for task_id in task_ids:
        task = AsyncResult(task_id)
        tasks.append({
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None
        })
    
    return tasks



# Новый маршрут для проверки статуса задачи и получения `transcription_id`
@status_bp.route('/transcription/status/<task_id>', methods=['GET'])
@jwt_required()
def get_transcription_status(task_id):
    task = process_and_transcribe_audio_task.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {'status': 'pending'}
    elif task.state == 'SUCCESS':
        response = {
            'status': 'completed',
            'transcription_id': task.result  # `transcription_id` будет возвращен задачей после завершения
        }
    else:
        response = {'status': 'failed'}
    
    return jsonify(response)
