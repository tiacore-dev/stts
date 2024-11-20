"""from service_registry import get_service
import json
import time
import threading


sockets = get_service('sockets')
redis_client=get_service('redis')

# Прогресс хранится в Redis
PROGRESS_KEY = 'task_progress'"""

"""# Функция для обработки прогресса задачи
def process_task(ws, task_id):
    # Отправляем начальное сообщение о начале задачи
    redis_client.set(PROGRESS_KEY, json.dumps({
        'status': 'started',
        'message': 'Задача началась.'
    }))
    ws.send(json.dumps({
        'status': 'started',
        'message': 'Задача началась.'
    }))

    # Этапы обработки задачи
    for stage in ['processing', 'channel_1', 'channel_2']:
        # Обновляем прогресс в Redis
        redis_client.set(PROGRESS_KEY, json.dumps({
            'status': 'in_progress',
            'stage': stage
        }))
        
        # Отправляем прогресс по WebSocket
        ws.send(json.dumps({
            'status': 'in_progress',
            'stage': stage
        }))
        time.sleep(1)  # Имитация паузы для каждого этапа

    # Завершение задачи
    redis_client.set(PROGRESS_KEY, json.dumps({
        'status': 'completed',
        'message': 'Задача завершена.'
    }))
    ws.send(json.dumps({
        'status': 'completed',
        'message': 'Задача завершена.'
    }))


# WebSocket-обработчик
@sockets.route('/progress')
def progress_socket(ws):
    task_id = None  # Задача, которую клиент будет отслеживать
    
    while True:
        message = ws.receive()
        if message:
            data = json.loads(message)
            task_id = data.get('task_id')  # Получаем идентификатор задачи от клиента
            print(f"Received message: {data}")
            
            # Запускаем обработку задачи в отдельном потоке
            threading.Thread(target=process_task, args=(ws, task_id)).start()
            break  # После запуска задачи завершаем цикл приема сообщений"""