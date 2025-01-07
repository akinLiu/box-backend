"""认证服务模块"""
from typing import Optional, Tuple
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.base import db

class AuthService:
    """认证服务类"""
    
    @staticmethod
    def register(username: str, password: str, email: str, role: str = 'user') -> Tuple[Optional[User], Optional[str]]:
        """注册用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            role: 角色，默认为 'user'
            
        Returns:
            Tuple[Optional[User], Optional[str]]: (用户对象, 错误信息)
            如果注册成功，错误信息为 None
        """
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return None, '用户名已存在'
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return None, '邮箱已存在'
            
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        user.save()
        return user, None
    
    @staticmethod
    def login(username: str, password: str) -> Tuple[Optional[str], Optional[str]]:
        """用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (token, 错误信息)
            如果登录成功，错误信息为 None
        """
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return None, '用户不存在'
            
        if not user.check_password(password):
            return None, '密码错误'
            
        token = create_access_token(identity=str(user.id))
        return token, None
    
    @staticmethod
    def get_users(page: int = 1, per_page: int = 10) -> Tuple[list, int]:
        """获取用户列表
        
        Args:
            page: 页码，默认为 1
            per_page: 每页数量，默认为 10
            
        Returns:
            Tuple[list, int]: (用户列表, 总用户数)
        """
        pagination = User.query.paginate(page=page, per_page=per_page)
        return pagination.items, pagination.total
    
    @staticmethod
    def update_user(user_id: int, data: dict) -> Tuple[Optional[User], Optional[str]]:
        """更新用户信息
        
        Args:
            user_id: 用户 ID
            data: 更新数据
            
        Returns:
            Tuple[Optional[User], Optional[str]]: (用户对象, 错误信息)
            如果更新成功，错误信息为 None
        """
        user = db.session.get(User, user_id)
        if not user:
            return None, '用户不存在'
            
        if 'username' in data:
            existing = User.query.filter(
                User.username == data['username'],
                User.id != user_id
            ).first()
            if existing:
                return None, '用户名已存在'
            user.username = data['username']
            
        if 'email' in data:
            existing = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing:
                return None, '邮箱已存在'
            user.email = data['email']
            
        if 'role' in data:
            user.role = data['role']
            
        if 'password' in data:
            user.set_password(data['password'])
            
        db.session.commit()
        return user, None
