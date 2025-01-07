import pytest
import json
from app import create_app
from app.models.base import db
from app.models.user import User
from app.models.device import Device, DeviceUserAssociation

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
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')
    admin.save()
    
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    return json.loads(response.data)['token']

@pytest.fixture
def user_token(client):
    user = User(username='testuser', email='test@example.com', role='user')
    user.set_password('user123')
    user.save()
    
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'user123'
    })
    return json.loads(response.data)['token']

def test_create_device(client, admin_token, user_token):
    """测试创建设备"""
    # 测试管理员创建设备
    headers = {'Authorization': f'Bearer {admin_token}'}
    device_data = {
        'name': 'test_device',
        'ip_address': '192.168.1.100',
        'mac_address': '00:11:22:33:44:55',
        'description': 'Test device',
        'tags': ['test', 'device']
    }
    
    response = client.post('/api/devices', 
                          headers=headers,
                          json=device_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == device_data['name']
    
    # 测试普通用户创建设备
    headers = {'Authorization': f'Bearer {user_token}'}
    response = client.post('/api/devices',
                          headers=headers,
                          json=device_data)
    assert response.status_code == 403

def test_get_devices(client, admin_token, user_token):
    """测试获取设备列表"""
    # 创建测试设备
    device = Device(
        name='test_device',
        ip_address='192.168.1.100',
        mac_address='00:11:22:33:44:55',
        description='Test device'
    )
    device.save()
    
    # 测试管理员访问
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/devices', headers=headers)
    assert response.status_code == 200
    devices = json.loads(response.data)
    assert len(devices) == 1
    
    # 测试普通用户访问
    headers = {'Authorization': f'Bearer {user_token}'}
    response = client.get('/api/devices', headers=headers)
    assert response.status_code == 200
    devices = json.loads(response.data)
    assert len(devices) == 0

def test_update_device(client, admin_token, user_token):
    """测试更新设备"""
    # 创建测试设备
    device = Device(
        name='test_device',
        ip_address='192.168.1.100',
        mac_address='00:11:22:33:44:55',
        description='Test device'
    )
    device.save()
    
    update_data = {
        'name': 'updated_device',
        'description': 'Updated test device'
    }
    
    # 测试管理员更新
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.put(f'/api/devices/{device.id}',
                         headers=headers,
                         json=update_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == update_data['name']
    
    # 测试未授权用户更新
    headers = {'Authorization': f'Bearer {user_token}'}
    response = client.put(f'/api/devices/{device.id}',
                         headers=headers,
                         json=update_data)
    assert response.status_code == 403

def test_device_authorization(client, admin_token):
    """测试设备授权"""
    # 创建测试设备和用户
    device = Device(
        name='test_device',
        ip_address='192.168.1.100',
        mac_address='00:11:22:33:44:55',
        description='Test device'
    )
    device.save()
    
    user = User(username='testuser2', email='test2@example.com', role='user')
    user.set_password('password123')
    user.save()
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post(f'/api/devices/{device.id}/authorize',
                          headers=headers,
                          json={'user_id': user.id})
    assert response.status_code == 200
    
    # 验证授权结果
    association = db.session.query(DeviceUserAssociation).filter_by(
        device_id=device.id,
        user_id=user.id
    ).first()
    assert association is not None
