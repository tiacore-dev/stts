from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

#app, socketio = create_app()




if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)