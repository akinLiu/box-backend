"""设备 API 测试模块"""
import pytest
from app.models.device import Device, DeviceUserAssociation
from app.models.base import db

def clean_device_data(app, device_name):
    """清理设备相关数据"""
    with app.app_context():
        device = Device.query.filter_by(name=device_name).first()
        if device:
            # 先删除关联记录
            DeviceUserAssociation.query.filter_by(device_id=device.id).delete()
            db.session.commit()
            # 再删除设备
            Device.query.filter_by(id=device.id).delete()
            db.session.commit()

def test_create_device(client, admin_token):
    """测试创建设备"""
    # 清理测试数据
    clean_device_data(client.application, 'test_device')

    # 创建设备
    response = client.post(
        '/api/devices',
        json={
            'name': 'test_device',
            'ip_address': '192.168.1.100',
            'mac_address': '00:11:22:33:44:55',
            'description': 'Test device',
            'tags': ['test', 'device']
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert data['message'] == '设备创建成功'
    assert data['data']['name'] == 'test_device'
    assert data['data']['ip_address'] == '192.168.1.100'
    assert data['data']['mac_address'] == '00:11:22:33:44:55'
    assert data['data']['description'] == 'Test device'
    assert data['data']['tags'] == ['test', 'device']

    # 验证数据库中的数据
    with client.application.app_context():
        device = Device.query.filter_by(name='test_device').first()
        assert device is not None
        assert device.name == 'test_device'
        assert device.ip_address == '192.168.1.100'
        assert device.mac_address == '00:11:22:33:44:55'
        assert device.description == 'Test device'
        assert device.tags == 'test,device'

def test_get_devices(client, admin_token, normal_user_token):
    """测试获取设备列表"""
    # 清理测试数据
    clean_device_data(client.application, 'test_device')

    # 创建测试设备
    with client.application.app_context():
        device = Device(
            name='test_device',
            ip_address='192.168.1.100',
            mac_address='00:11:22:33:44:55',
            description='Test device',
            tags='test,device'
        )
        db.session.add(device)
        db.session.commit()

    # 管理员获取设备列表
    response = client.get(
        '/api/devices',
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']) >= 1
    assert any(d['name'] == 'test_device' for d in data['data'])

    # 普通用户获取设备列表
    response = client.get(
        '/api/devices',
        headers={'Authorization': f'Bearer {normal_user_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']) == 0

def test_update_device(client, admin_token):
    """测试更新设备"""
    # 清理测试数据
    clean_device_data(client.application, 'test_device')

    # 创建测试设备
    with client.application.app_context():
        device = Device(
            name='test_device',
            ip_address='192.168.1.100',
            mac_address='00:11:22:33:44:55',
            description='Test device',
            tags='test,device'
        )
        db.session.add(device)
        db.session.commit()

        device_id = device.id

    # 更新设备
    response = client.put(
        f'/api/devices/{device_id}',
        json={
            'name': 'updated_device',
            'description': 'Updated description',
            'tags': ['updated', 'test']
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert data['data']['name'] == 'updated_device'
    assert data['data']['description'] == 'Updated description'
    assert data['data']['tags'] == ['updated', 'test']

    # 验证数据库中的数据
    with client.application.app_context():
        device = Device.query.filter_by(id=device_id).first()
        assert device is not None
        assert device.name == 'updated_device'
        assert device.description == 'Updated description'
        assert device.tags == 'updated,test'

def test_authorize_device(client, admin_token, normal_user):
    """测试授权设备"""
    # 清理测试数据
    clean_device_data(client.application, 'test_device')

    # 创建测试设备
    with client.application.app_context():
        device = Device(
            name='test_device',
            ip_address='192.168.1.100',
            mac_address='00:11:22:33:44:55',
            description='Test device',
            tags='test,device'
        )
        db.session.add(device)
        db.session.commit()

        device_id = device.id

    # 授权设备给普通用户
    response = client.post(
        f'/api/devices/{device_id}/authorize',
        json={
            'user_id': normal_user.id,
            'permission_type': 'read'
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200

def test_batch_authorize_by_tags(client, admin_token, normal_user):
    """测试批量授权设备"""
    # 清理并创建测试设备
    with client.application.app_context():
        Device.query.filter(Device.name.like('test_device%')).delete()
        DeviceUserAssociation.query.delete()
        db.session.commit()

        # 创建多个测试设备
        for i in range(3):
            device = Device(
                name=f'test_device_{i}',
                ip_address=f'192.168.1.{100+i}',
                mac_address=f'00:11:22:33:44:{55+i:02x}',
                description=f'Test device {i}',
                tags=f'test,device_{i}'
            )
            db.session.add(device)
        db.session.commit()

    # 批量授权设备
    response = client.post(
        '/api/devices/batch_authorize',
        json={
            'tags': ['test', 'device_0'],
            'user_id': normal_user.id,
            'permission_type': 'read'
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
