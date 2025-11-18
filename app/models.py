from flask_login import UserMixin
from . import db  # ✅ Import db from the package, not from app.__init__.py directly

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # optional but good practice

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
