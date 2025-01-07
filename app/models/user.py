from werkzeug.security import generate_password_hash, check_password_hash
from .base import db, BaseModel

class User(db.Model, BaseModel):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, user
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        """重写序列化方法，排除密码哈希"""
        result = super().to_dict()
        result.pop('password_hash', None)
        return result
        
    def __repr__(self):
        return f'<User {self.username}>'
