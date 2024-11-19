
from flask_jwt_extended import create_access_token
from flask import jsonify, request, Blueprint, render_template
from flask_jwt_extended import create_refresh_token, get_jwt_identity, verify_jwt_in_request



login_bp = Blueprint('login', __name__)


# Основная страница
@login_bp.route('/')
def index():
    return render_template('auth/home.html')

# Маршрут для страницы входа
@login_bp.route('/login', methods=['GET'])
def login():
    return render_template('auth/login.html')


# Маршрут для страницы входа
@login_bp.route('/register', methods=['GET'])
def register():
    return render_template('auth/register.html')

# Выход из системы
@login_bp.route('/logout')
def logout():
    return jsonify({"msg": "Logout successful"}), 200



# Маршрут для входа (авторизации)
@login_bp.route('/auth', methods=['POST'])
def auth():
    from app.database.managers.user_manager import UserManager
    # Создаем экземпляр менеджера базы данных
    db = UserManager()
    login = request.json.get("login", None)
    password = request.json.get("password", None)

    # Проверяем пользователя в базе данных
    if not db.user_exists(login) or not db.check_password(login, password):
        return {"msg": "Bad username or password"}, 401

    user_id = db.get_user_id(login)
    # Генерируем Access и Refresh токены с дополнительной информацией
    
    identity = {
        "user_id": user_id,
        "login": login
    }

    access_token = str(create_access_token(identity=identity))
    refresh_token = str(create_refresh_token(identity=identity))


    return jsonify(access_token=access_token, refresh_token=refresh_token), 200



@login_bp.route('/register', methods=['POST'])
def register_user():
    from app.database.managers.user_manager import UserManager
    # Создаем экземпляр менеджера базы данных
    db = UserManager()
    username = request.json.get('username', None)
    login = request.json.get('login', None)
    password = request.json.get('password', None)

    if not login or not password:
        return jsonify({"msg": "Login and password are required"}), 400

    if db.user_exists(login):
        return jsonify({"msg": "Login already taken"}), 400

    user_id = db.add_user(username, login, password)

        # Генерируем JWT токен
    
    # Генерируем Access и Refresh токены с дополнительной информацией
    identity = {
        "user_id": user_id,
        "login": login
    }

    access_token = str(create_access_token(identity=identity))
    refresh_token = str(create_refresh_token(identity=identity))
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    

@login_bp.route('/refresh', methods=['POST'])
def refresh():
    # Получение токена из тела запроса
    refresh_token = request.json.get('refresh_token', None)
    if not refresh_token:
        return jsonify({"msg": "Missing refresh token"}), 400

    try:
        # Явная валидация токена
        verify_jwt_in_request(refresh=True, locations=["json"])
    except Exception as e:
        return jsonify({"msg": str(e)}), 401

    # Получение текущего пользователя
    current_user = get_jwt_identity()

    # Генерация нового access токена
    new_access_token = str(create_access_token(identity=current_user))
    new_refresh_token = str(create_refresh_token(identity = current_user))
    return jsonify(access_token= new_access_token, refresh_token= new_refresh_token), 200