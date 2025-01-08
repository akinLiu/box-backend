from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app.models.user import User
from app.models.base import db
from app.utils.response import Response
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
@cross_origin()
def register():
    """
    注册用户
    :return:
    """
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return Response.validation_error('缺少必要字段')
            
        user, error = AuthService.register(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            role=data.get('role', 'user')
        )
        
        if error:
            return Response.error(error)
            
        return Response.success(user.to_dict(), '注册成功')
    except Exception as e:
        current_app.logger.error(f"Register error: {str(e)}")
        return Response.error('注册失败，请稍后重试', 500)

@auth_bp.route('/login', methods=['POST'])
@cross_origin()
def login():
    """
    用户登录
    :return:
    """
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'password')):
            return Response.validation_error('缺少必要字段')
        
        token, error = AuthService.login(
            username=data['username'],
            password=data['password']
        )
        
        if error:
            return Response.error(error, 401)
            
        return Response.success({
            'token': token, 
            'user': User.query.filter_by(username=data['username']).first().to_dict()
        }, '登录成功')
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return Response.error('登录失败，请稍后重试', 500)

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@cross_origin()
def get_users():
    """
    获取用户列表
    :return:
    """
    try:
        user_id = get_jwt_identity()
        print(f"JWT identity: {user_id}, type: {type(user_id)}")
        
        with current_app.app_context():
            current_user = db.session.get(User, int(user_id))
            print(f"Current user: {current_user}, role: {current_user.role if current_user else None}")
            
            if not current_user or current_user.role != 'admin':
                return Response.forbidden()
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            users, total = AuthService.get_users(page, per_page)
            
            return Response.success({
                'items': [user.to_dict() for user in users],
                'total': total,
                'page': page,
                'per_page': per_page
            })
    except Exception as e:
        current_app.logger.error(f"Get users error: {str(e)}")
        return Response.error('获取用户列表失败，请稍后重试', 500)

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@cross_origin()
def update_user(user_id):
    """
    更新用户信息
    :param user_id:
    :return:
    """
    try:
        user_id_str = get_jwt_identity()
        print(f"JWT identity: {user_id_str}, type: {type(user_id_str)}")
        
        with current_app.app_context():
            current_user = db.session.get(User, int(user_id_str))
            print(f"Current user: {current_user}, role: {current_user.role if current_user else None}")
            
            if not current_user or current_user.role != 'admin':
                return Response.forbidden()
            
            data = request.get_json()
            if not data:
                return Response.validation_error('没有提供更新数据')
            
            user, error = AuthService.update_user(user_id, data)
            if error:
                return Response.error(error)
                
            return Response.success(user.to_dict(), '用户信息更新成功')
    except Exception as e:
        current_app.logger.error(f"Update user error: {str(e)}")
        return Response.error('更新用户信息失败，请稍后重试', 500)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    获取当前用户资料
    :return:
    """
    try:
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))
        
        if not user:
            return Response.error('用户不存在', 404)
            
        return Response.success(user.to_dict())
    except Exception as e:
        current_app.logger.error(f"Get profile error: {str(e)}")
        return Response.error('获取用户资料失败', 500)
