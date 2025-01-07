"""测试配置文件"""
import pytest
from flask_jwt_extended import create_access_token
from app import create_app
from app.models.base import db
from app.models.user import User

@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    app = create_app('testing')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 清理所有数据
        User.query.delete()
        db.session.commit()
        
        # 创建管理员用户
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        admin.save()
    
    yield app
    
    # 清理数据库
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建测试命令运行器"""
    return app.test_cli_runner()

@pytest.fixture
def admin_token(app):
    """创建管理员 token"""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        return create_access_token(identity=str(admin.id))

@pytest.fixture(autouse=True)
def clean_users(app):
    """自动清理用户数据（每个测试前）"""
    with app.app_context():
        # 保留管理员用户，删除其他用户
        User.query.filter(User.username != 'admin').delete()
        db.session.commit()
        
    yield
    
    # 测试后清理
    with app.app_context():
        User.query.filter(User.username != 'admin').delete()
        db.session.commit()
