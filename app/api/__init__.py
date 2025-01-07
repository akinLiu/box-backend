from flask import Blueprint

api_bp = Blueprint('api', __name__)

from .auth import auth_bp
from .device import device_bp

# 注册子蓝图，不需要添加/api前缀，因为这个前缀已经在app/__init__.py中添加了
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(device_bp)
