from flask import jsonify
from typing import Any, Dict, List, Optional, Union

class Response:
    """统一的响应格式工具类"""
    
    @staticmethod
    def success(data: Optional[Union[Dict, List]] = None, message: str = "操作成功") -> Dict:
        """成功响应"""
        response = {
            "code": 200,
            "message": message,
            "data": data
        }
        return jsonify(response)
    
    @staticmethod
    def error(message: str, code: int = 400, data: Optional[Dict] = None) -> Dict:
        """错误响应"""
        response = {
            "code": code,
            "message": message,
            "data": data
        }
        return jsonify(response), code
    
    @staticmethod
    def forbidden(message: str = "权限不足") -> Dict:
        """权限不足响应"""
        return Response.error(message, 403)
    
    @staticmethod
    def not_found(message: str = "资源不存在") -> Dict:
        """资源不存在响应"""
        return Response.error(message, 404)
    
    @staticmethod
    def validation_error(message: str = "输入验证错误", errors: Optional[Dict] = None) -> Dict:
        """输入验证错误响应"""
        return Response.error(message, 422, errors)
