"""Flask 应用工厂模块"""
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import config
from app.utils.jwt_handlers import register_jwt_error_handlers

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    """应用工厂函数
    
    Args:
        config_name: 配置名称，默认为 'default'
        
    Returns:
        Flask 应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 注册 JWT 错误处理器
    register_jwt_error_handlers(jwt)
    
    # 注册蓝图
    from .api import api_bp
    from app.api.auth import auth_bp
    from app.api.dashboard import dashboard_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    
    # 注册命令
    from .commands import register_commands
    register_commands(app)
    
    return app
