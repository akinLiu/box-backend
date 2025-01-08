"""仪表盘相关接口"""
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.models.device import Device, DeviceUserAssociation
from app.models.user import User
from app.utils.response import Response

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取仪表盘统计数据
    
    Returns:
        JSON: 统计数据
    """
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role == 'admin':
            # 管理员可以看到所有设备
            device_count = Device.query.count()
        else:
            # 普通用户只能看到有权限的设备
            device_count = Device.query.join(
                DeviceUserAssociation,
                Device.id == DeviceUserAssociation.device_id
            ).filter(
                DeviceUserAssociation.user_id == current_user_id
            ).distinct().count()
        
        # 获取设备状态统计
        if current_user.role == 'admin':
           status_stats = dict(
                Device.query.with_entities(
                    Device.status,
                    func.count(Device.id)
                ).group_by(Device.status).all()
            ) 
        else:
            status_stats = dict(
                Device.query.join(
                    DeviceUserAssociation,
                    Device.id == DeviceUserAssociation.device_id
                ).filter(
                    DeviceUserAssociation.user_id == current_user_id
                ).with_entities(
                    Device.status,
                    func.count(Device.id)
                ).group_by(Device.status).all()
            )
        
        return Response.success({
            'deviceCount': device_count,
            'statusStats': {
                'online': status_stats.get('online', 0),
                'offline': status_stats.get('offline', 0)
            }
        })
    except Exception as e:
        return Response.error(str(e), 500)
