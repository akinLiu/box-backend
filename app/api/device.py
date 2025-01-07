from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.device import Device, DeviceUserAssociation
from app.models.base import db
from app.utils.response import Response
from app.services.device_service import DeviceService

device_bp = Blueprint('device', __name__, url_prefix='/devices')

@device_bp.route('', methods=['POST'])
@jwt_required()
def create_device():
    current_user = db.session.get(User, get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return Response.forbidden()
    
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'ip_address', 'mac_address')):
        return Response.validation_error('缺少必要字段')
    
    device = DeviceService.create_device(data)
    return Response.success(device.to_dict(), '设备创建成功')

@device_bp.route('', methods=['GET'])
@jwt_required()
def get_devices():
    current_user = db.session.get(User, get_jwt_identity())
    if not current_user:
        return Response.not_found('用户不存在')
    
    devices = DeviceService.get_devices(current_user.id, current_user.role == 'admin')
    return Response.success([device.to_dict() for device in devices])

@device_bp.route('/<int:device_id>', methods=['PUT'])
@jwt_required()
def update_device(device_id):
    current_user = db.session.get(User, get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return Response.forbidden()
    
    data = request.get_json()
    if not data:
        return Response.validation_error('没有提供更新数据')
    
    device = DeviceService.update_device(device_id, data)
    if not device:
        return Response.not_found('设备不存在')
    
    return Response.success(device.to_dict(), '设备更新成功')

@device_bp.route('/<int:device_id>/authorize', methods=['POST'])
@jwt_required()
def authorize_device(device_id):
    current_user = db.session.get(User, get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return Response.forbidden()
    
    data = request.get_json()
    if not data or 'user_id' not in data:
        return Response.validation_error('缺少用户ID')
    
    association = DeviceService.authorize_device(
        device_id=device_id,
        user_id=data['user_id'],
        permission_type=data.get('permission_type', 'read')
    )
    
    if not association:
        return Response.error('该用户已被授权访问此设备', 400)
    
    return Response.success(None, '设备授权成功')

@device_bp.route('/<int:device_id>/authorize/batch', methods=['POST'])
@jwt_required()
def batch_authorize_by_tags(device_id):
    current_user = db.session.get(User, get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return Response.forbidden()
    
    data = request.get_json()
    if not data or not all(k in data for k in ('tags', 'user_id')):
        return Response.validation_error('缺少必要字段')
    
    if not data['tags']:
        return Response.validation_error('没有提供标签')
    
    associations = DeviceService.batch_authorize_by_tags(
        tags=data['tags'],
        user_id=data['user_id'],
        permission_type=data.get('permission_type', 'read')
    )
    
    return Response.success(
        {'count': len(associations)},
        f'成功授权 {len(associations)} 个设备'
    )
