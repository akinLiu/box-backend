"""设备 API 测试模块"""
import pytest
from flask_jwt_extended import create_access_token
from app.models.device import Device, DeviceUserAssociation
from app.models.user import User
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
    assert len(data['data']['items']) >= 1
    assert any(d['name'] == 'test_device' for d in data['data']['items'])
    
    # 普通用户获取设备列表
    response = client.get(
        '/api/devices',
        headers={'Authorization': f'Bearer {normal_user_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 0

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

def test_search_devices_by_name(client, admin_token):
    """测试按名称搜索设备"""
    # 清理并创建测试设备
    with client.application.app_context():
        Device.query.delete()
        DeviceUserAssociation.query.delete()
        db.session.commit()

        # 创建测试设备
        devices = [
            Device(
                name='测试设备1',
                ip_address='192.168.1.1',
                mac_address='00:11:22:33:44:55',
                status='online',
                tags='dp,test'
            ),
            Device(
                name='测试设备2',
                ip_address='192.168.1.2',
                mac_address='00:11:22:33:44:66',
                status='offline',
                tags='dp'
            ),
            Device(
                name='生产设备1',
                ip_address='192.168.1.3',
                mac_address='AA:BB:CC:DD:EE:FF',
                status='online',
                tags='prod'
            )
        ]
        for device in devices:
            db.session.add(device)
        db.session.commit()

    # 精确匹配
    response = client.get(
        '/api/devices?name=测试设备1',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 1
    assert data['data']['items'][0]['name'] == '测试设备1'

    # 模糊匹配
    response = client.get(
        '/api/devices?name=测试',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 2

def test_search_devices_by_status(client, admin_token):
    """测试按状态搜索设备"""
    # 使用相同的测试数据
    with client.application.app_context():
        Device.query.delete()
        DeviceUserAssociation.query.delete()
        db.session.commit()

        devices = [
            Device(
                name='测试设备1',
                ip_address='192.168.1.1',
                mac_address='00:11:22:33:44:55',
                status='online',
                tags='dp,test'
            ),
            Device(
                name='测试设备2',
                ip_address='192.168.1.2',
                mac_address='00:11:22:33:44:66',
                status='offline',
                tags='dp'
            ),
            Device(
                name='生产设备1',
                ip_address='192.168.1.3',
                mac_address='AA:BB:CC:DD:EE:FF',
                status='online',
                tags='prod'
            )
        ]
        for device in devices:
            db.session.add(device)
        db.session.commit()

    # 测试在线状态
    response = client.get(
        '/api/devices?status=online',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 2

    # 测试离线状态
    response = client.get(
        '/api/devices?status=offline',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 1

def test_search_devices_by_tags(client, admin_token):
    """测试按标签搜索设备"""
    # 使用相同的测试数据
    with client.application.app_context():
        Device.query.delete()
        DeviceUserAssociation.query.delete()
        db.session.commit()

        devices = [
            Device(
                name='测试设备1',
                ip_address='192.168.1.1',
                mac_address='00:11:22:33:44:55',
                status='online',
                tags='dp,test'
            ),
            Device(
                name='测试设备2',
                ip_address='192.168.1.2',
                mac_address='00:11:22:33:44:66',
                status='offline',
                tags='dp'
            ),
            Device(
                name='生产设备1',
                ip_address='192.168.1.3',
                mac_address='AA:BB:CC:DD:EE:FF',
                status='online',
                tags='prod'
            )
        ]
        for device in devices:
            db.session.add(device)
        db.session.commit()

    # 单个标签搜索
    response = client.get(
        '/api/devices?tags[]=dp',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 2

    # 多个标签搜索
    response = client.get(
        '/api/devices?tags[]=dp&tags[]=test',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 2

def test_search_devices_combined(client, admin_token):
    """测试组合条件搜索设备"""
    # 使用相同的测试数据
    with client.application.app_context():
        Device.query.delete()
        DeviceUserAssociation.query.delete()
        db.session.commit()

        devices = [
            Device(
                name='测试设备1',
                ip_address='192.168.1.1',
                mac_address='00:11:22:33:44:55',
                status='online',
                tags='dp,test'
            ),
            Device(
                name='测试设备2',
                ip_address='192.168.1.2',
                mac_address='00:11:22:33:44:66',
                status='offline',
                tags='dp'
            ),
            Device(
                name='生产设备1',
                ip_address='192.168.1.3',
                mac_address='AA:BB:CC:DD:EE:FF',
                status='online',
                tags='prod'
            )
        ]
        for device in devices:
            db.session.add(device)
        db.session.commit()

    # 名称 + 状态
    response = client.get(
        '/api/devices?name=测试&status=online',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 1
    assert data['data']['items'][0]['name'] == '测试设备1'

    # 标签 + 状态
    response = client.get(
        '/api/devices?tags[]=dp&status=offline',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 1
    assert data['data']['items'][0]['name'] == '测试设备2'

    # 名称 + 标签 + 状态
    response = client.get(
        '/api/devices?name=测试&tags[]=dp&status=online',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) == 1
    assert data['data']['items'][0]['name'] == '测试设备1'
