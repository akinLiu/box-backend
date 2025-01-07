"""设备服务模块"""
from typing import List, Optional
from app.models.device import Device, DeviceUserAssociation
from app.models.user import User
from app.models.base import db

class DeviceService:
    """设备服务类"""
    
    @staticmethod
    def create_device(data: dict) -> Device:
        """创建设备"""
        # 将标签列表转换为逗号分隔的字符串
        tags = data.get('tags', [])
        tags_str = ','.join(tags) if tags else ''
        
        device = Device(
            name=data['name'],
            ip_address=data['ip_address'],
            mac_address=data['mac_address'],
            description=data.get('description', ''),
            tags=tags_str
        )
        db.session.add(device)
        db.session.commit()
        return device
    
    @staticmethod
    def get_devices(user_id: int, is_admin: bool) -> List[Device]:
        """获取设备列表"""
        if is_admin:
            return Device.query.all()
        return [assoc.device for assoc in 
                DeviceUserAssociation.query.filter_by(user_id=user_id).all()]
    
    @staticmethod
    def update_device(device_id: int, data: dict) -> Optional[Device]:
        """更新设备信息"""
        device = db.session.get(Device, device_id)
        if not device:
            return None
            
        if 'name' in data:
            device.name = data['name']
        if 'ip_address' in data:
            device.ip_address = data['ip_address']
        if 'mac_address' in data:
            device.mac_address = data['mac_address']
        if 'description' in data:
            device.description = data['description']
        if 'tags' in data:
            device.tags = ','.join(data['tags']) if data['tags'] else ''
        
        db.session.commit()
        return device
    
    @staticmethod
    def authorize_device(device_id: int, user_id: int, permission_type: str = 'read') -> Optional[DeviceUserAssociation]:
        """授权设备给用户"""
        # 检查设备和用户是否存在
        device = db.session.get(Device, device_id)
        user = db.session.get(User, user_id)
        if not device or not user:
            return None
            
        # 检查是否已经授权
        existing = DeviceUserAssociation.query.filter_by(
            device_id=device.id,
            user_id=user.id
        ).first()
        if existing:
            return None
            
        association = DeviceUserAssociation(
            device_id=device.id,
            user_id=user.id,
            permission_type=permission_type
        )
        db.session.add(association)
        db.session.commit()
        return association
    
    @staticmethod
    def batch_authorize_by_tags(tags: List[str], user_id: int, permission_type: str = 'read') -> List[DeviceUserAssociation]:
        """根据标签批量授权设备"""
        devices = []
        for tag in tags:
            devices.extend(Device.query.filter(Device.tags.like(f'%{tag}%')).all())
        devices = list(set(devices))  # 去重
        
        associations = []
        for device in devices:
            existing = DeviceUserAssociation.query.filter_by(
                device_id=device.id,
                user_id=user_id
            ).first()
            
            if existing:
                existing.permission_type = permission_type
            else:
                assoc = DeviceUserAssociation(
                    device_id=device.id,
                    user_id=user_id,
                    permission_type=permission_type
                )
                db.session.add(assoc)
                associations.append(assoc)
                
        db.session.commit()
        return associations
