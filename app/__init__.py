from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import config

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)
    
    # 加载配置
    app.config.from_object(config[config_name])
    app.config.from_pyfile('config.py', silent=True)
    
    # 配置 SQLAlchemy 2.0
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 注册蓝图
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 注册命令
    from .commands import register_commands
    register_commands(app)
    
    return app
