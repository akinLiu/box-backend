from .base import db, BaseModel

class Device(db.Model, BaseModel):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(15))
    mac_address = db.Column(db.String(17))
    status = db.Column(db.String(20), default='offline')
    description = db.Column(db.String(200))
    tags = db.Column(db.String(200))
    
    def to_dict(self):
        """重写序列化方法，处理tags字段"""
        result = super().to_dict()
        if result['tags']:
            result['tags'] = result['tags'].split(',')
        else:
            result['tags'] = []
        return result

class DeviceUserAssociation(db.Model, BaseModel):
    __tablename__ = 'device_user_associations'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_type = db.Column(db.String(20), nullable=False)  # read, write
    
    device = db.relationship('Device', backref=db.backref('user_associations', lazy=True))
    user = db.relationship('User', backref=db.backref('device_associations', lazy=True))
