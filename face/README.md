# JoyRent 人脸识别模块

## 📋 概述

JoyRent人脸识别模块基于Python Flask + FaceNet,为JoyRent游戏租赁平台提供人脸识别登录功能。

## 🗄️ 数据库配置

### 数据库信息
- **数据库名**: `joy_rent`
- **用户表**: `users`
- **人脸表**: `user_face`

### 配置文件
编辑 `database_config.py` 修改数据库连接信息:

```python
class DatabaseConfig:
    def __init__(self):
        self.host = 'localhost'
        self.port = 3306
        self.user = 'root'
        self.password = '123456'  # 修改为你的密码
        self.database = 'joy_rent'
        self.charset = 'utf8mb4'
```

## 🚀 启动服务

### 1. 安装依赖

```bash
cd face
pip install -r requirements.txt
```

### 2. 启动Flask服务

```bash
python api_server_db.py
```

服务将在 `http://localhost:5000` 启动

## 📡 API接口

### 健康检查
```
GET /api/health
```

### 人脸注册
```
POST /api/user/face/register
Body: {
  "user_id": 1,
  "image": "base64_encoded_image"
}
```

### 人脸登录
```
POST /api/user/face/login
Body: {
  "image": "base64_encoded_image"
}
```

### 禁用人脸识别
```
POST /api/user/face/disable
Body: {
  "user_id": 1
}
```

### 获取人脸用户列表
```
GET /api/users/face
```

## 🔧 前端集成

在 `switchRentApp/api/face.js` 中已封装好所有API调用:

```javascript
import { faceLogin, registerFace, disableFace } from '@/api/face';

// 人脸登录
const result = await faceLogin(base64Image);

// 人脸注册
const result = await registerFace(userId, base64Image);

// 禁用人脸
const result = await disableFace(userId);
```

## 📊 数据库表结构

### users 表
- `id` - 用户ID
- `username` - 用户名
- `phone` - 手机号
- `password` - 密码(MD5)
- `nickname` - 昵称
- `avatar` - 头像
- `role` - 角色(10=普通用户, 20=管理员)
- `balance` - 余额
- `status` - 状态(1=启用, 0=禁用)

### user_face 表
- `user_id` - 用户ID
- `face_encoding` - 人脸特征向量(JSON格式)

## ⚠️ 注意事项

1. **用户注册**: 用户注册由Spring Boot后端处理,不使用Flask API
2. **密码登录**: 密码登录由Spring Boot后端处理,不使用Flask API
3. **人脸识别**: 仅人脸识别相关功能使用Flask API
4. **数据库**: 确保`joy_rent`数据库已创建并包含正确的表结构
5. **端口**: Flask服务默认运行在5000端口,确保端口未被占用

## 🔐 安全建议

1. 修改 `api_server_db.py` 中的 `SECRET_KEY`
2. 生产环境中使用HTTPS
3. 添加请求频率限制
4. 定期备份人脸数据

## 📝 更新日志

### v2.0 - 2025-11-30
- ✅ 适配JoyRent数据库结构
- ✅ 使用`joy_rent`数据库
- ✅ 更新用户字段映射(phone, nickname, role)
- ✅ 移除用户注册和密码登录接口
- ✅ 简化角色管理
