"""测试配置模块"""
import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.device import DeviceUserAssociation
from app.models.base import db

@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    from app import create_app
    app = create_app('testing')
    
    # 创建数据库表（如果不存在）
    with app.app_context():
        db.create_all()
    
    return app

@pytest.fixture(scope='session')
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(app):
    """创建管理员用户"""
    with app.app_context():
        # 清理已存在的管理员
        User.query.filter_by(username='admin').delete()
        db.session.commit()
        
        # 创建新管理员
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        # 刷新会话以确保实例被正确加载
        db.session.refresh(admin)
        return admin

@pytest.fixture(scope='function')
def admin_token(app, admin_user):
    """创建管理员 token"""
    with app.app_context():
        return create_access_token(identity=str(admin_user.id))

@pytest.fixture(scope='function')
def normal_user(app):
    """创建普通用户"""
    with app.app_context():
        # 清理已存在的测试用户
        User.query.filter_by(username='testuser').delete()
        db.session.commit()
        
        # 创建新测试用户
        user = User(
            username='testuser',
            email='test@example.com',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # 刷新会话以确保实例被正确加载
        db.session.refresh(user)
        return user

@pytest.fixture(scope='function')
def normal_user_token(app, normal_user):
    """创建普通用户 token"""
    with app.app_context():
        return create_access_token(identity=str(normal_user.id))

@pytest.fixture(autouse=True)
def clean_users(app):
    """清理测试用户数据（每个测试前）"""
    yield
    with app.app_context():
        # 先删除关联记录
        test_users = User.query.filter(User.username != 'admin').all()
        for user in test_users:
            DeviceUserAssociation.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        # 再删除用户
        User.query.filter(User.username != 'admin').delete()
        db.session.commit()
