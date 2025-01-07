import pytest
import json
from app.models.user import User
from app.models.base import db

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """创建管理员用户，如果不存在的话"""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            admin.save()
        return admin

@pytest.fixture
def admin_token(client, admin_user):
    """获取管理员的 JWT token"""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    data = json.loads(response.data)
    return data['token']

def test_register(client):
    """测试用户注册"""
    # 检查用户是否已存在，如果存在则删除
    with client.application.app_context():
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

    # 测试注册新用户
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['username'] == 'testuser'
    assert data['email'] == 'test@example.com'
    assert data['role'] == 'user'

    # 测试重复注册
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400

def test_login(client):
    """测试用户登录"""
    # 确保测试用户存在
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@example.com', role='user')
            user.set_password('password123')
            user.save()

    # 测试正确的用户名和密码
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert data['user']['username'] == 'testuser'

    # 测试错误的密码
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_get_users(client, admin_token):
    """测试获取用户列表"""
    # 确保测试用户存在
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@example.com', role='user')
            user.set_password('password123')
            user.save()

    # 测试管理员访问
    response = client.get('/api/auth/users',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 2  # 至少包含 admin 和 testuser

def test_update_user(client, admin_token):
    """测试更新用户信息"""
    # 确保测试用户存在
    user_id = None
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@example.com', role='user')
            user.set_password('password123')
            user.save()
        user_id = user.id

    # 测试管理员更新用户信息
    headers = {'Authorization': f'Bearer {admin_token}'}
    update_data = {
        'username': 'updated_user',
        'email': 'updated@example.com',
        'role': 'admin'
    }

    response = client.put(f'/api/auth/users/{user_id}',
                         headers=headers,
                         json=update_data)
    assert response.status_code == 200

    # 验证更新结果
    with client.application.app_context():
        updated_user = db.session.get(User, user_id)  
        assert updated_user.username == 'updated_user'
        assert updated_user.email == 'updated@example.com'
        assert updated_user.role == 'admin'

        # 清理：恢复用户原始状态
        updated_user.username = 'testuser'
        updated_user.email = 'test@example.com'
        updated_user.role = 'user'
        db.session.commit()
