import click
from flask.cli import with_appcontext
from . import db
from .models.user import User

def register_commands(app):
    """注册 Flask CLI 命令"""
    
    @app.cli.command('init-db')
    @with_appcontext
    def init_db():
        """初始化数据库"""
        click.echo('创建数据库表...')
        db.create_all()
        click.echo('数据库表创建完成。')
        
    @app.cli.command('create-admin')
    @with_appcontext
    def create_admin():
        """创建管理员用户"""
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
            
    @app.cli.command('reset-db')
    @with_appcontext
    def reset_db():
        """重置数据库"""
        if click.confirm('确定要删除所有数据吗？'):
            click.echo('删除数据库表...')
            db.drop_all()
            click.echo('创建数据库表...')
            db.create_all()
            click.echo('数据库重置完成。')
