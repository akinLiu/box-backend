"""认证 API 测试模块"""
import pytest
import json
from flask_jwt_extended import create_access_token
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
    return data['data']['token']

def test_register(client):
    """测试用户注册"""
    # 清理测试数据
    with client.application.app_context():
        User.query.filter(User.username.in_(['testuser', 'testuser2'])).delete()
        User.query.filter(User.email.in_(['test@example.com', 'test2@example.com'])).delete()
        db.session.commit()
        
    # 测试正常注册
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '注册成功'
    assert data['data']['username'] == 'testuser'
    assert data['data']['email'] == 'test@example.com'
    
    # 测试重复用户名
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert '用户名已存在' in data['message']
    
    # 测试重复邮箱
    response = client.post('/api/auth/register', json={
        'username': 'testuser2',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert '邮箱已存在' in data['message']
    
    # 测试缺少必要字段
    response = client.post('/api/auth/register', json={
        'username': 'testuser'
    })
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data['code'] == 422
    assert '缺少必要字段' in data['message']

def test_login(client):
    """测试用户登录"""
    # 清理测试数据
    with client.application.app_context():
        User.query.filter_by(username='testuser').delete()
        db.session.commit()
        
    # 创建测试用户
    with client.application.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        user.save()
    
    # 测试正常登录
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '登录成功'
    assert 'token' in data['data']
    assert data['data']['user']['username'] == 'testuser'
    
    # 测试错误密码
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['code'] == 401
    assert '密码错误' in data['message']
    
    # 测试不存在的用户
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'password123'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['code'] == 401
    assert '用户不存在' in data['message']
    
    # 测试缺少必要字段
    response = client.post('/api/auth/login', json={
        'username': 'testuser'
    })
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data['code'] == 422
    assert '缺少必要字段' in data['message']

def test_get_users(client, admin_token):
    """测试获取用户列表"""
    # 清理测试数据
    with client.application.app_context():
        User.query.filter(User.username.startswith('testuser')).delete()
        db.session.commit()
        
    # 创建一些测试用户
    with client.application.app_context():
        for i in range(3):
            user = User(
                username=f'testuser{i}',
                email=f'test{i}@example.com',
                role='user'
            )
            user.set_password('password123')
            user.save()
    
    # 测试管理员获取用户列表
    response = client.get('/api/auth/users',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'items' in data['data']
    assert 'total' in data['data']
    assert 'page' in data['data']
    assert 'per_page' in data['data']
    assert len(data['data']['items']) == 4  # 3个测试用户 + 1个管理员
    
    # 测试非管理员获取用户列表
    with client.application.app_context():
        user = User.query.filter_by(username='testuser0').first()
        token = create_access_token(identity=str(user.id))
    
    response = client.get('/api/auth/users',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['code'] == 403
    assert '权限不足' in data['message']

def test_update_user(client, admin_token):
    """测试更新用户信息"""
    # 清理测试数据
    with client.application.app_context():
        User.query.filter(User.username.in_(['testuser', 'updated_user'])).delete()
        User.query.filter(User.email.in_(['test@example.com', 'updated@example.com'])).delete()
        db.session.commit()
        
    # 创建测试用户
    with client.application.app_context():
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
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '用户信息更新成功'
    assert data['data']['username'] == 'updated_user'
    assert data['data']['email'] == 'updated@example.com'
    assert data['data']['role'] == 'admin'

    # 测试非管理员更新用户信息
    with client.application.app_context():
        normal_user = User(username='normaluser', email='normal@example.com', role='user')
        normal_user.set_password('password123')
        normal_user.save()
        normal_token = create_access_token(identity=str(normal_user.id))

    response = client.put(f'/api/auth/users/{user_id}',
                         headers={'Authorization': f'Bearer {normal_token}'},
                         json=update_data)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['code'] == 403
    assert '权限不足' in data['message']

    # 测试更新不存在的用户
    response = client.put('/api/auth/users/99999',
                         headers=headers,
                         json=update_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert '用户不存在' in data['message']
