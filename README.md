# Box 后端服务

Box后端服务是一个基于Python Flask框架开发的RESTful API服务。

## 项目架构

```
backend/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用初始化
│   ├── models/            # 数据模型
│   ├── api/               # API蓝图和路由
│   ├── schemas/           # 序列化模式
│   ├── services/          # 业务逻辑层
│   └── utils/             # 工具函数
├── tests/                 # 测试目录
├── config.py              # 配置文件
├── requirements.txt       # 项目依赖
└── run.py                # 应用入口
```

## 技术栈

- Python 3.9+
- Flask 2.x
- SQLAlchemy 2.x
- MySQL 8.0
- JWT认证
- pytest测试框架

## 功能特性

- RESTful API设计
- JWT用户认证与授权
- 数据库ORM操作
- 单元测试与集成测试
- 错误处理与日志记录
- API文档自动生成

## 本地开发环境部署

1. 创建并激活Python虚拟环境:
```bash
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
```

2. 安装项目依赖:
```bash
pip install -r requirements.txt
```

3. 配置环境变量:
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
```

4. 初始化数据库:
```bash
flask db upgrade
```

5. 运行开发服务器:
```bash
flask run
```

## 服务器部署

1. 系统要求:
- Linux服务器
- Python 3.9+
- MySQL 8.0
- Nginx

2. 安装依赖:
```bash
pip install -r requirements.txt
pip install gunicorn
```

3. 配置Gunicorn服务:
```bash
# /etc/systemd/system/box-backend.service
[Unit]
Description=Box Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

4. 配置Nginx:
```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. 启动服务:
```bash
sudo systemctl start box-backend
sudo systemctl enable box-backend
sudo systemctl restart nginx
```

## 开发规范

- 遵循PEP 8 Python代码规范
- 使用类型注解
- 编写完整的函数文档
- 保持良好的测试覆盖率
- 遵循RESTful API设计原则

## 测试

运行测试:
```bash
pytest
```

生成测试覆盖率报告:
```bash
pytest --cov=app tests/
```
