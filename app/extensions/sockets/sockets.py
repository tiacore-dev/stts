# app/sockets.py
from service_registry import get_service
import json


# Инициализация WebSocket
sockets = get_service('sockets')

# Словарь для отслеживания подключений по логинам
clients = {}

def send_progress(user_id, message):
    """Отправка сообщения всем подключенным клиентам для указанного пользователя"""
    for login, ws_list in clients.items():
        # Найдем все соединения для этого логина
        for ws in ws_list:
            try:
                # Отправка сообщения, если оно связано с данным user_id
                if ws.user_id == user_id:
                    ws.send(json.dumps(message))
            except:
                continue

# WebSocket маршрут
@sockets.route('/progress/<login>')
def handle_socket(ws, login):
    """Подключение пользователя к WebSocket для получения прогресса"""
    from app.database.managers.user_manager import UserManager
    # Проверка пользователя в базе данных по логину
    db = UserManager()
    user = db.get_user_id(login)
    
    if user is None:
        # Если пользователь не найден, закрываем соединение
        ws.send(json.dumps({"status": "error", "message": "User not found"}))
        ws.close()
        return
    
    # Присваиваем user_id текущему WebSocket-соединению
    ws.user_id = user
    
    # Добавляем WebSocket в список клиентов
    if login not in clients:
        clients[login] = []
    
    clients[login].append(ws)
    
    try:
        # Ожидание сообщений от клиента, если нужно
        while True:
            message = ws.receive()
            if message is None:
                break
    finally:
        # Удаляем WebSocket-соединение при отключении
        clients[login].remove(ws)
        if not clients[login]:
            del clients[login]
