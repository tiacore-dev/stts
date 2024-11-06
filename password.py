import os
from dotenv import load_dotenv
from app.database import init_db, set_db_globals

load_dotenv()

password=os.getenv('PASSWORD')
username=os.getenv('LOGIN')
database_url = os.getenv('DATABASE_URL')

engine, Session, Base = init_db(database_url)

    # Установка глобальных переменных для работы с базой данных
set_db_globals(engine, Session, Base)


from app.database.managers.user_manager import UserManager
db = UserManager()


if db.user_exists(username):
    db.delete_user(username)

db.add_user(username, password)
print('New admin added successfully')