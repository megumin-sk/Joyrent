from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import cv2
import io
from PIL import Image
import os
import pymysql
import json
import hashlib
from datetime import datetime, timedelta
import jwt

from face_recognition_service import FaceRecognitionService
from database_config import db_manager

app = Flask(__name__)
CORS(app)

# JWT配置
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
JWT_EXPIRATION_HOURS = 24

# 初始化人脸识别服务
face_service = FaceRecognitionService()

def generate_token(user_info):
    """生成JWT令牌"""
    payload = {
        'user_id': user_info['id'],
        'username': user_info['username'],
        'phone': user_info.get('phone'),
        'nickname': user_info.get('nickname'),
        'role': user_info.get('role', 10),
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def base64_to_image(base64_string):
    """将base64字符串转换为OpenCV图像"""
    try:
        # 检查输入是否为空
        if not base64_string:
            print("Base64转图像失败: 输入字符串为空")
            return None
        
        # 移除data:image前缀（如果存在）
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # 检查base64字符串长度
        if len(base64_string) < 100:  # 一个有效的图像base64应该很长
            print(f"Base64转图像失败: base64字符串太短 (长度: {len(base64_string)})")
            return None
        
        # 解码base64
        try:
            image_data = base64.b64decode(base64_string)
        except Exception as decode_error:
            print(f"Base64转图像失败: base64解码错误 - {decode_error}")
            return None
        
        # 检查解码后的数据长度
        if len(image_data) < 1000:  # 图像数据应该足够大
            print(f"Base64转图像失败: 解码后数据太小 (长度: {len(image_data)})")
            return None
        
        # 转换为PIL图像
        try:
            pil_image = Image.open(io.BytesIO(image_data))
        except Exception as pil_error:
            print(f"Base64转图像失败: PIL图像打开错误 - {pil_error}")
            return None
        
        # 转换为OpenCV格式
        try:
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as cv_error:
            print(f"Base64转图像失败: OpenCV转换错误 - {cv_error}")
            return None
        
        print(f"Base64转图像成功: 图像尺寸 {opencv_image.shape}")
        return opencv_image
        
    except Exception as e:
        print(f"Base64转图像失败: 未知错误 - {e}")
        return None

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db_status = db_manager.test_connection()
        
        # 获取启用人脸识别的用户数量
        face_users = db_manager.get_all_face_users()
        
        return jsonify({
            'status': 'ok',
            'message': '数据库版本的人脸识别API服务正在运行',
            'database_status': '已连接' if db_status else '未连接',
            'face_enabled_users': len(face_users),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Health check failed: {str(e)}'
        }), 500

# 用户注册接口已禁用 - JoyRent使用Spring Boot后端处理用户注册
# @app.route('/api/user/register', methods=['POST'])
# def register_user():
#     """用户注册"""
#     pass
#     try:
#         data = request.get_json()
        
#         # 验证必需字段
#         required_fields = ['username', 'password', 'real_name']
#         for field in required_fields:
#             if not data.get(field):
#                 return jsonify({
#                     'success': False,
#                     'message': f'缺少必需字段: {field}'
#                 }), 400
        
#         # 检查用户名是否已存在
#         existing_user = db_manager.get_user_by_username(data['username'])
#         if existing_user:
#             return jsonify({
#                 'success': False,
#                 'message': '用户名已存在'
#             }), 400
        
#         # 创建用户
#         hashed_password = hash_password(data['password'])
#         user_id = db_manager.create_user(
#             username=data['username'],
#             password=hashed_password,
#             full_name=data['real_name'],
#             email=data.get('email'),
#             phone=data.get('phone'),
#             role_id=data.get('role_id')
#         )
        
#         if user_id:
#             return jsonify({
#                 'success': True,
#                 'message': '用户注册成功',
#                 'user_id': user_id
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'message': '用户注册失败'
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'注册失败: {str(e)}'
#         }), 500

@app.route('/api/user/face/register', methods=['POST'])
def register_user_face():
    """用户人脸注册"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('user_id') or not data.get('image'):
            return jsonify({
                'success': False,
                'message': '缺少必需字段: user_id 或 image'
            }), 400
        
        user_id = data['user_id']
        
        # 验证用户是否存在
        user = db_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 转换图像
        image = base64_to_image(data['image'])
        if image is None:
            return jsonify({
                'success': False,
                'message': '图像格式错误'
            }), 400
        
        # 提取人脸特征 (numpy array)
        face_encoding = face_service._encode_face(image)
        if face_encoding is None:
            return jsonify({
                'success': False,
                'message': '未检测到人脸或人脸质量不佳'
            }), 400
        
        # 将 numpy array 转换为 list 以便 JSON 序列化
        encoding_list = face_encoding.tolist()
        
        # 保存图像文件到本地 (用于可视化调试或后续处理，非必须可由Java决定)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            face_images_dir = os.path.join(current_dir, 'face_images')
            os.makedirs(face_images_dir, exist_ok=True)
            img_filename = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            img_path = os.path.join(face_images_dir, img_filename)
            cv2.imwrite(img_path, image)
        except:
            pass

        return jsonify({
            'success': True,
            'message': '人脸特征提取成功',
            'face_encoding': encoding_list,
            'user_id': user_id
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'人脸注册失败: {str(e)}'
        }), 500

@app.route('/api/user/face/register/upload', methods=['POST'])
def register_user_face_upload():
    """用户人脸注册 - 文件上传版本"""
    try:
        # 获取表单数据
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少必需字段: user_id'
            }), 400
        
        # 获取上传的文件
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': '缺少图片文件'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '未选择文件'
            }), 400
        
        # 验证用户是否存在
        user = db_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 读取图像文件
        try:
            image_data = file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({
                    'success': False,
                    'message': '图像格式不支持'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'图像读取失败: {str(e)}'
            }), 400
        
        # 提取人脸特征
        face_encoding = face_service._encode_face(image)
        if face_encoding is None:
            return jsonify({
                'success': False,
                'message': '未检测到人脸或人脸质量不佳'
            }), 400
        
        # 保存到数据库
        img_url = f"/face_images/{user['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        success = db_manager.save_user_face_embedding(user_id, face_encoding, img_url)
        
        if success:
            # 保存图像文件到本地
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                face_images_dir = os.path.join(current_dir, 'face_images')
                os.makedirs(face_images_dir, exist_ok=True)
                img_filename = f"{user['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                img_path = os.path.join(face_images_dir, img_filename)
                cv2.imwrite(img_path, image)
            except:
                pass  # 忽略文件保存错误
            
            return jsonify({
                'success': True,
                'message': f'用户 {user.get("nickname") or user["username"]} 人脸注册成功',
                'userInfo': {
                    'id': user['id'],
                    'username': user['username'],
                    'phone': user.get('phone'),
                    'nickname': user.get('nickname'),
                    'avatar': user.get('avatar'),
                    'role': user.get('role', 10),
                    'balance': float(user.get('balance', 0))
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '人脸特征保存失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'人脸注册失败: {str(e)}'
        }), 500

@app.route('/api/user/login', methods=['POST'])
def user_login():
    """用户密码登录"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': '缺少用户名或密码'
            }), 400
        
        # 查询用户
        user = db_manager.get_user_by_username(data['username'])
        if not user:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 验证密码
        hashed_password = hash_password(data['password'])
        if user['password'] != hashed_password:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 生成令牌
        token = generate_token(user)
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'userInfo': {
                'id': user['id'],
                'username': user['username'],
                'phone': user.get('phone'),
                'nickname': user.get('nickname'),
                'avatar': user.get('avatar'),
                'role': user.get('role', 10),
                'balance': float(user.get('balance', 0)),
                'face_enabled': bool(user['face_enabled'])
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@app.route('/api/user/face/login', methods=['POST'])
def face_login():
    """人脸识别登录"""
    try:
        data = request.get_json()
        
        if not data.get('image'):
            return jsonify({
                'success': False,
                'message': '缺少图像数据'
            }), 400
        
        # 转换图像
        image = base64_to_image(data['image'])
        if image is None:
            return jsonify({
                'success': False,
                'message': '图像格式错误'
            }), 400
        
        # 获取所有启用人脸识别的用户
        face_users = db_manager.get_all_face_users()
        if not face_users:
            return jsonify({
                'success': False,
                'message': '系统中没有启用人脸识别的用户'
            }), 404
        
        # 构建人脸数据库
        known_faces = {}
        for user in face_users:
            if user['face_embedding'] is not None:
                known_faces[user['username']] = user['face_embedding']
        
        if not known_faces:
            return jsonify({
                'success': False,
                'message': '没有有效的人脸数据'
            }), 404
        
        # 临时更新人脸服务的已知人脸
        original_known_face_encodings = face_service.known_face_encodings.copy()
        original_known_face_names = face_service.known_face_names.copy()
        
        # 更新人脸服务的已知人脸数据
        face_service.known_face_encodings = []
        face_service.known_face_names = []
        
        for username, embedding in known_faces.items():
            face_service.known_face_encodings.append(embedding)
            face_service.known_face_names.append(username)
        
        try:
            # 进行人脸识别
            print(f"开始人脸识别，已知人脸数量: {len(known_faces)}")
            result = face_service.recognize_face(image)
            print(f"人脸识别完成，结果: {result}")
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'message': result['message']
                }), 400
            
            faces_info = result['faces']
            if not faces_info:
                return jsonify({
                    'success': False,
                    'message': '未检测到人脸'
                }), 400
            
            # 查找识别成功的用户
            recognized_user = None
            for face_info in faces_info:
                print(f"检测到人脸: {face_info.get('name', 'Unknown')}, 置信度: {face_info.get('confidence', 0)}")
                if face_info['name'] != 'Unknown':
                    name = face_info['name']
                    # 优先假设这是一个 face_id (UUID)
                    # 尝试通过 face_id 在 user_face 表中查找真实的本地 ID
                    with db_manager.get_connection() as conn:
                        cursor = conn.cursor(pymysql.cursors.DictCursor)
                        # 查找关联的 user_id
                        cursor.execute("SELECT user_id FROM user_face WHERE face_id = %s", (name,))
                        mapping = cursor.fetchone()
                        
                        if mapping:
                            # 找到了关联，通过 user_id 获取完整信息
                            recognized_user = db_manager.get_user_by_id(mapping['user_id'])
                        else:
                            # 如果没找到关联，回退到按用户名查找（兼容旧数据）
                            recognized_user = db_manager.get_user_by_username(name)
                    
                    if recognized_user:
                        print(f"找到匹配用户: {recognized_user['username']} (ID: {recognized_user['id']})")
                        break
            
            if recognized_user:
                # 生成令牌
                token = generate_token(recognized_user)
                
                return jsonify({
                    'success': True,
                    'message': f'人脸识别登录成功，欢迎 {recognized_user.get("nickname") or recognized_user["username"]}',
                    'token': token,
                    'userInfo': {
                        'id': recognized_user['id'],
                        'username': recognized_user['username'],
                        'phone': recognized_user.get('phone'),
                        'nickname': recognized_user.get('nickname'),
                        'avatar': recognized_user.get('avatar'),
                        'role': recognized_user.get('role', 10),
                        'balance': float(recognized_user.get('balance', 0)),
                        'face_enabled': bool(recognized_user['face_enabled'])
                    },
                    'recognition_confidence': faces_info[0]['confidence']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '人脸识别失败，未找到匹配用户'
                }), 401
                
        finally:
            # 恢复原始人脸数据
            face_service.known_face_encodings = original_known_face_encodings
            face_service.known_face_names = original_known_face_names
            
    except Exception as e:
        print(f"人脸登录异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'人脸登录失败: {str(e)}'
        }), 500

@app.route('/api/user/face/disable', methods=['POST'])
def disable_user_face():
    """禁用用户人脸识别"""
    try:
        data = request.get_json()
        
        if not data.get('user_id'):
            return jsonify({
                'success': False,
                'message': '缺少用户ID'
            }), 400
        
        success = db_manager.disable_user_face(data['user_id'])
        
        if success:
            return jsonify({
                'success': True,
                'message': '人脸识别已禁用'
            })
        else:
            return jsonify({
                'success': False,
                'message': '禁用失败，用户不存在'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'禁用失败: {str(e)}'
        }), 500

@app.route('/api/user/face/delete', methods=['POST'])
def delete_user_face():
    """完全删除用户人脸数据（用于注册失败回滚）"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少必需字段: user_id'}), 400
            
        user = db_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
            
        # 1. 数据库禁用/清除特征
        db_success = db_manager.disable_user_face(user_id)
        
        # 2. 调用逻辑层删除文件和内存数据
        face_service.delete_face(user['username'])
        
        return jsonify({
            'success': True,
            'message': f'用户 {user["username"]} 人脸数据已清理'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/face', methods=['GET'])
def get_face_users():
    """获取所有启用人脸识别的用户列表"""
    try:
        users = db_manager.get_all_face_users()
        
        # 只返回基本信息，不包含人脸特征数据
        user_list = []
        for user in users:
            user_list.append({
                'id': user['id'],
                'username': user['username'],
                'phone': user.get('phone'),
                'nickname': user.get('nickname')
            })
        
        return jsonify({
            'success': True,
            'users': user_list,
            'total': len(user_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

# 角色接口已禁用 - JoyRent使用简单的role字段
# @app.route('/api/roles', methods=['GET'])
# def get_roles():
#     """获取所有角色"""
#     pass


@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取当前用户信息（需要token）"""
    try:
        # 获取Authorization头
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '缺少认证令牌'
            }), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'message': '令牌无效或已过期'
            }), 401
        
        # 获取最新用户信息
        user = db_manager.get_user_by_id(payload['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'user_info': {
                'id': user['id'],
                'username': user['username'],
                'phone': user.get('phone'),
                'nickname': user.get('nickname'),
                'avatar': user.get('avatar'),
                'role': user.get('role', 10),
                'balance': float(user.get('balance', 0)),
                'face_enabled': bool(user['face_enabled']),
                'created_at': user['created_at'].isoformat() if user['created_at'] else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 启动人脸识别API服务器（数据库版本）...")
    print("📊 检查数据库连接...")
    
    if db_manager.test_connection():
        print("✅ 数据库连接成功")
        face_users = db_manager.get_all_face_users()
        print(f"👥 当前启用人脸识别的用户: {len(face_users)}")
        
        print("\n🌐 JoyRent人脸识别API接口:")
        print("  健康检查: GET /api/health")
        print("  人脸注册(JSON): POST /api/user/face/register")
        print("  人脸注册(文件): POST /api/user/face/register/upload")
        print("  人脸登录: POST /api/user/face/login")
        print("  禁用人脸: POST /api/user/face/disable")
        print("  人脸用户列表: GET /api/users/face")
        print("  用户信息: GET /api/user/info")
        print("\n🔗 服务地址: http://localhost:5000")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ 数据库连接失败，请检查配置")