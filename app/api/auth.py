from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.models.base import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 422
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        role='user'
    )
    user.set_password(data['password'])
    user.save()
    
    return jsonify(user.to_dict()), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'message': 'Missing username or password'}), 422
    
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'token': access_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'message': 'Invalid username or password'}), 401

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = get_jwt_identity()
    print(f"JWT identity: {user_id}, type: {type(user_id)}")
    
    with current_app.app_context():
        current_user = db.session.get(User, int(user_id))
        print(f"Current user: {current_user}, role: {current_user.role if current_user else None}")
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'message': 'Permission denied'}), 403
        
        result = db.session.execute(db.select(User))
        users = result.scalars().all()
        return jsonify([user.to_dict() for user in users]), 200

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user_id_str = get_jwt_identity()
    print(f"JWT identity: {user_id_str}, type: {type(user_id_str)}")
    
    with current_app.app_context():
        current_user = db.session.get(User, int(user_id_str))
        print(f"Current user: {current_user}, role: {current_user.role if current_user else None}")
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'message': 'Permission denied'}), 403
        
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
        
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
