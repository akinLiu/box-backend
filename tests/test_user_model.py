import pytest
from app.models.user import User
from app.models.base import db

def test_new_user():
    """测试创建新用户"""
    user = User(
        username='test_user',
        email='test@example.com',
        role='user'
    )
    user.set_password('password123')
    
    assert user.username == 'test_user'
    assert user.email == 'test@example.com'
    assert user.role == 'user'
    assert user.password_hash is not None
    
def test_password_hashing():
    """测试密码哈希功能"""
    user = User(username='test_user')
    user.set_password('password123')
    
    assert user.password_hash is not None
    assert user.check_password('password123') is True
    assert user.check_password('wrongpassword') is False
    
def test_user_to_dict():
    """测试用户数据序列化"""
    user = User(
        username='test_user',
        email='test@example.com',
        role='user'
    )
    user_dict = user.to_dict()
    
    assert user_dict['username'] == 'test_user'
    assert user_dict['email'] == 'test@example.com'
    assert user_dict['role'] == 'user'
    assert 'password_hash' not in user_dict
