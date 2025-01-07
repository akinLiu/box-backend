import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models.user import User
from app.models.device import Device, DeviceUserAssociation

app = create_app(os.getenv('FLASK_ENV') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Device=Device, DeviceUserAssociation=DeviceUserAssociation)

@app.cli.command()
@click.option('--drop', is_flag=True, help='先删除后创建')
def initdb(drop):
    """初始化数据库"""
    if drop:
        click.echo('删除数据库...')
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库完成。')

@app.cli.command()
def init():
    """初始化数据库并创建管理员账户"""
    click.echo('初始化数据库...')
    db.create_all()
    
    # 检查是否已存在管理员账户
    admin = User.query.filter_by(role='admin').first()
    if admin is None:
        click.echo('创建管理员账户...')
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        click.echo('管理员账户创建成功。')
    else:
        click.echo('管理员账户已存在。')
    
    click.echo('初始化完成。')
