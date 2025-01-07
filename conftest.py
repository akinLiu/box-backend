import os
import sys
import pytest
from app import create_app
from app.models.base import db

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    app.config['JWT_SECRET_KEY'] = 'test-jwt-key'  # 设置 JWT 密钥
    app.config['TESTING'] = True
    return app
