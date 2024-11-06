def admin(password, username, login):
    from app.database.managers.user_manager import UserManager
    db = UserManager()
    
    #if db.user_exists(username):
        #db.delete_user_by_username(username)

    db.add_user(username, login, password, user_type='admin')
    print('New admin added successfully')