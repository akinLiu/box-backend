import os
import sys
import pytest
import json
from app import create_app
from app.models.user import User
from app.models.base import db

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-jwt-key'  # 设置 JWT 密钥
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
    return app

@pytest.fixture(scope='session')
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture(scope='session')
def admin_user(app):
    """创建管理员用户"""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        return admin

@pytest.fixture(scope='session')
def admin_token(client, admin_user):
    """获取管理员的 JWT token"""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    data = json.loads(response.data)
    return data['token']
