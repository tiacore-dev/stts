"""from flask import Blueprint
from flask_socketio import emit, join_room, leave_room
from service_registry import get_service

socket_bp = Blueprint('socket', __name__)
socketio = get_service('socketio')

# Событие для подключения клиента
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('response', {'message': 'Connection established'})

# Событие для отключения клиента
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Пример события для получения сообщений от клиента
@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    emit('response', {'message': 'Message received'})

# Событие для работы с комнатами
@socketio.on('join')
def on_join(room):
    join_room(room)
    emit('response', {'message': f'Joined room {room}'}, room=room)

@socketio.on('leave')
def on_leave(room):
    leave_room(room)
    emit('response', {'message': f'Left room {room}'}, room=room)
"""