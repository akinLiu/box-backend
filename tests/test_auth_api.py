import pytest
import json
from app import create_app
from app.models.base import db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app('development')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_token(client):
    # 创建管理员用户
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')
    admin.save()
    
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    return json.loads(response.data)['token']

@pytest.fixture
def clean_db():
    db.session.remove()
    db.drop_all()
    db.create_all()

def test_register(client, clean_db):
    """测试用户注册"""
    # 测试正常注册
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    
    # 测试重复用户名
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    
    # 测试重复邮箱
    response = client.post('/api/auth/register', json={
        'username': 'testuser2',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400

def test_login(client, clean_db):
    """测试用户登录"""
    # 创建测试用户
    user = User(username='testuser', email='test@example.com', role='user')
    user.set_password('password123')
    user.save()
    
    # 测试正常登录
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert 'user' in data
    
    # 测试密码错误
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    
    # 测试不存在的用户
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'password123'
    })
    assert response.status_code == 401

def test_get_users(client, admin_token, clean_db):
    """测试获取用户列表"""
    # 创建测试用户
    user = User(username='testuser', email='test@example.com', role='user')
    user.set_password('password123')
    user.save()
    
    # 测试管理员访问
    response = client.get('/api/auth/users', 
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    users = json.loads(response.data)
    assert len(users) == 2  # admin + testuser
    
    # 测试普通用户访问
    user_response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    user_token = json.loads(user_response.data)['token']
    
    response = client.get('/api/auth/users',
                         headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 403  # 权限不足

def test_update_user(client, admin_token, clean_db):
    """测试更新用户信息"""
    # 创建测试用户
    user = User(username='testuser', email='test@example.com', role='user')
    user.set_password('password123')
    user.save()
    
    # 测试管理员更新用户信息
    headers = {'Authorization': f'Bearer {admin_token}'}
    update_data = {
        'username': 'updated_user',
        'email': 'updated@example.com',
        'role': 'admin'
    }
    
    response = client.put(f'/api/auth/users/{user.id}',
                         headers=headers,
                         json=update_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == update_data['username']
    assert data['email'] == update_data['email']
    assert data['role'] == update_data['role']
    
    # 测试普通用户更新管理员信息
    user_response = client.post('/api/auth/login', json={
        'username': 'updated_user',
        'password': 'password123'
    })
    user_token = json.loads(user_response.data)['token']
    
    response = client.put(f'/api/auth/users/1',  # admin的ID为1
                         headers={'Authorization': f'Bearer {user_token}'},
                         json={'username': 'hacked'})
    assert response.status_code == 403  # 权限不足
