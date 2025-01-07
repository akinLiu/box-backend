"""JWT 错误处理模块"""
from app.utils.response import Response

def register_jwt_error_handlers(jwt):
    """注册 JWT 错误处理器"""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return Response.error('Token 已过期', 401)
        
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return Response.error('无效的 Token', 401)
        
    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return Response.error('缺少 Token', 401)
        
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return Response.error('需要新的 Token', 401)
        
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return Response.error('Token 已被撤销', 401)
