from flask import Blueprint
from flask_socketio import SocketIO, emit, join_room, leave_room

socket_routes = Blueprint('socket_routes', __name__)

# Событие для подключения клиента
@socket_routes.on('connect')
def handle_connect():
    print("Client connected")
    emit('response', {'message': 'Connection established'})

# Событие для отключения клиента
@socket_routes.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Пример события для получения сообщений от клиента
@socket_routes.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    emit('response', {'message': 'Message received'})
    
# Событие для работы с комнатами (если нужно)
@socket_routes.on('join')
def on_join(room):
    join_room(room)
    emit('response', {'message': f'Joined room {room}'}, room=room)

@socket_routes.on('leave')
def on_leave(room):
    leave_room(room)
    emit('response', {'message': f'Left room {room}'}, room=room)
