import pytest
from app.models.device import Device, DeviceUserAssociation
from app.models.user import User
from app.models.base import db

def test_new_device():
    """测试创建新设备"""
    device = Device(
        name='test_device',
        ip_address='192.168.1.100',
        mac_address='00:11:22:33:44:55',
        status='offline',
        description='Test device description',
        tags='test,device'
    )
    
    assert device.name == 'test_device'
    assert device.ip_address == '192.168.1.100'
    assert device.mac_address == '00:11:22:33:44:55'
    assert device.status == 'offline'
    assert device.description == 'Test device description'
    assert device.tags == 'test,device'
    
def test_device_to_dict():
    """测试设备数据序列化"""
    device = Device(
        name='test_device',
        ip_address='192.168.1.100',
        mac_address='00:11:22:33:44:55',
        status='offline',
        description='Test device description',
        tags='test,device'
    )
    device_dict = device.to_dict()
    
    assert device_dict['name'] == 'test_device'
    assert device_dict['ip_address'] == '192.168.1.100'
    assert device_dict['mac_address'] == '00:11:22:33:44:55'
    assert device_dict['status'] == 'offline'
    assert device_dict['description'] == 'Test device description'
    assert device_dict['tags'] == ['test', 'device']

def test_device_user_association():
    """测试设备用户关联"""
    user = User(username='test_user', email='test@example.com', role='user')
    device = Device(
        name='test_device',
        ip_address='192.168.1.100',
        mac_address='00:11:22:33:44:55'
    )
    
    association = DeviceUserAssociation(
        device=device,
        user=user,
        permission_type='read'
    )
    
    assert association.device == device
    assert association.user == user
    assert association.permission_type == 'read'
