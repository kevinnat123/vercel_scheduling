from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, user_data):
        self.id = username
        self.user_data = user_data
