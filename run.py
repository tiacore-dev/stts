import eventlet
eventlet.monkey_patch()


from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

#app, socketio = create_app()


port = os.getenv('FLASK_PORT')

if __name__ == "__main__":
    app, socketio= create_app()
    socketio.run(app, host="0.0.0.0", port=port, debug=True)