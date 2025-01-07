from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.device import Device, DeviceUserAssociation
from app.models.base import db

device_bp = Blueprint('device', __name__, url_prefix='/devices')

@device_bp.route('', methods=['POST'])
@jwt_required()
def create_device():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'ip_address', 'mac_address')):
        return jsonify({'message': 'Missing required fields'}), 422
    
    device = Device(
        name=data['name'],
        ip_address=data['ip_address'],
        mac_address=data['mac_address'],
        description=data.get('description', ''),
        tags=data.get('tags', [])
    )
    db.session.add(device)
    db.session.commit()
    
    return jsonify(device.to_dict()), 201

@device_bp.route('', methods=['GET'])
@jwt_required()
def get_devices():
    current_user = User.query.get(get_jwt_identity())
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    if current_user.role == 'admin':
        devices = Device.query.all()
    else:
        devices = [assoc.device for assoc in current_user.device_associations]
    
    return jsonify([device.to_dict() for device in devices]), 200

@device_bp.route('/<int:device_id>', methods=['PUT'])
@jwt_required()
def update_device(device_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': 'Permission denied'}), 403
    
    device = Device.query.get_or_404(device_id)
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 422
    
    if 'name' in data:
        device.name = data['name']
    if 'ip_address' in data:
        device.ip_address = data['ip_address']
    if 'mac_address' in data:
        device.mac_address = data['mac_address']
    if 'description' in data:
        device.description = data['description']
    if 'tags' in data:
        device.tags = data['tags']
    
    db.session.commit()
    return jsonify(device.to_dict()), 200

@device_bp.route('/<int:device_id>/authorize', methods=['POST'])
@jwt_required()
def authorize_device(device_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'message': 'Missing user_id'}), 422
    
    device = Device.query.get_or_404(device_id)
    user = User.query.get_or_404(data['user_id'])
    
    # 检查是否已经授权
    if DeviceUserAssociation.query.filter_by(
        device_id=device.id,
        user_id=user.id
    ).first():
        return jsonify({'message': 'Device already authorized for this user'}), 400
    
    association = DeviceUserAssociation(device_id=device.id, user_id=user.id)
    db.session.add(association)
    db.session.commit()
    
    return jsonify({'message': 'Device authorized successfully'}), 200

@device_bp.route('/<int:device_id>/authorize/batch', methods=['POST'])
@jwt_required()
def batch_authorize_by_tags(device_id):
    data = request.get_json()
    tags = data.get('tags', [])
    
    if not tags:
        return jsonify({'message': 'No tags provided'}), 400
        
    devices = db.session.query(Device).filter(
        Device.tags.like(f'%{tag}%') for tag in tags
    ).all()
    
    for device in devices:
        existing_assoc = db.session.query(DeviceUserAssociation).filter_by(
            device_id=device.id,
            user_id=data['user_id']
        ).first()
        
        if existing_assoc:
            existing_assoc.permission_type = data['permission_type']
            db.session.commit()
        else:
            assoc = DeviceUserAssociation(
                device_id=device.id,
                user_id=data['user_id'],
                permission_type=data['permission_type']
            )
            db.session.add(assoc)
            db.session.commit()
    
    return jsonify({'message': f'Authorized {len(devices)} devices successfully'})
