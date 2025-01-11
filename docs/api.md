# Linux设备管理系统 API 文档

## 基础信息

- 基础URL: `http://localhost:5000`
- 认证方式: JWT Token (在请求头中添加 `Authorization: Bearer <token>`)
- 响应格式: JSON

## 通用响应格式

```json
{
    "code": 200,       // 状态码
    "message": "成功",  // 响应消息
    "data": {}         // 响应数据
}
```

## 1. 认证相关 API

### 1.1 用户注册

- **接口**: `/auth/register`
- **方法**: `POST`
- **描述**: 注册新用户
- **请求体**:
  ```json
  {
    "username": "string",  // 用户名
    "email": "string",     // 邮箱
    "password": "string",  // 密码
    "role": "string"       // 角色(可选，默认为"user")
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "注册成功",
    "data": {
      "id": 1,
      "username": "string",
      "email": "string",
      "role": "string"
    }
  }
  ```

### 1.2 用户登录

- **接口**: `/auth/login`
- **方法**: `POST`
- **描述**: 用户登录获取token
- **请求体**:
  ```json
  {
    "username": "string",  // 用户名
    "password": "string"   // 密码
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "token": "string",
      "user": {
        "id": 1,
        "username": "string",
        "email": "string",
        "role": "string"
      }
    }
  }
  ```

### 1.3 获取用户列表

- **接口**: `/auth/users`
- **方法**: `GET`
- **描述**: 获取用户列表（仅管理员可用）
- **权限**: 需要管理员权限
- **查询参数**:
  - `page`: 页码（默认1）
  - `per_page`: 每页数量（默认10）
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "items": [
        {
          "id": 1,
          "username": "string",
          "email": "string",
          "role": "string"
        }
      ],
      "total": 100,
      "page": 1,
      "per_page": 10
    }
  }
  ```

### 1.4 更新用户信息

- **接口**: `/auth/users/<user_id>`
- **方法**: `PUT`
- **描述**: 更新用户信息（仅管理员可用）
- **权限**: 需要管理员权限
- **请求体**:
  ```json
  {
    "username": "string",  // 可选
    "email": "string",     // 可选
    "role": "string"       // 可选
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "用户信息更新成功",
    "data": {
      "id": 1,
      "username": "string",
      "email": "string",
      "role": "string"
    }
  }
  ```

## 2. 设备管理 API

### 2.1 创建设备

- **接口**: `/devices`
- **方法**: `POST`
- **描述**: 创建新设备（仅管理员可用）
- **权限**: 需要管理员权限
- **请求体**:
  ```json
  {
    "name": "string",        // 设备名称
    "ip_address": "string",  // IP地址
    "mac_address": "string"  // MAC地址
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "设备创建成功",
    "data": {
      "id": 1,
      "name": "string",
      "ip_address": "string",
      "mac_address": "string",
      "status": "string"
    }
  }
  ```

### 2.2 获取设备列表

- **接口**: `/devices`
- **方法**: `GET`
- **描述**: 获取设备列表
- **权限**: 需要登录
- **说明**: 管理员可以看到所有设备，普通用户只能看到被授权的设备
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": [
      {
        "id": 1,
        "name": "string",
        "ip_address": "string",
        "mac_address": "string",
        "status": "string"
      }
    ]
  }
  ```

### 2.3 更新设备信息

- **接口**: `/devices/<device_id>`
- **方法**: `PUT`
- **描述**: 更新设备信息（仅管理员可用）
- **权限**: 需要管理员权限
- **请求体**:
  ```json
  {
    "name": "string",        // 可选
    "ip_address": "string",  // 可选
    "mac_address": "string"  // 可选
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "设备更新成功",
    "data": {
      "id": 1,
      "name": "string",
      "ip_address": "string",
      "mac_address": "string",
      "status": "string"
    }
  }
  ```

### 2.4 设备授权

- **接口**: `/devices/<device_id>/authorize`
- **方法**: `POST`
- **描述**: 授权设备给用户（仅管理员可用）
- **权限**: 需要管理员权限
- **请求体**:
  ```json
  {
    "user_id": 1,                     // 用户ID
    "permission_type": "read"         // 权限类型（可选，默认为"read"）
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "设备授权成功",
    "data": null
  }
  ```

### 2.5 批量设备授权

- **接口**: `/devices/batch_authorize`
- **方法**: `POST`
- **描述**: 根据标签批量授权设备（仅管理员可用）
- **权限**: 需要管理员权限
- **请求体**:
  ```json
  {
    "tags": ["tag1", "tag2"],        // 标签列表
    "user_id": 1,                    // 用户ID
    "permission_type": "read"        // 权限类型（可选，默认为"read"）
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "成功授权 n 个设备",
    "data": {
      "count": 5
    }
  }
  ```

## 3. 仪表盘 API

### 3.1 获取统计数据

- **接口**: `/dashboard/statistics`
- **方法**: `GET`
- **描述**: 获取仪表盘统计数据
- **权限**: 需要登录
- **说明**: 管理员可以看到所有设备的统计，普通用户只能看到被授权设备的统计
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "deviceCount": 100,
      "statusStats": {
        "online": 80,
        "offline": 20
      }
    }
  }
  ```

## 错误码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误 