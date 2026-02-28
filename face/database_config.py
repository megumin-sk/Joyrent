import pymysql
import json
import numpy as np
from contextlib import contextmanager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """数据库配置类"""
    def __init__(self):
        self.host = 'localhost'
        self.port = 3306
        self.user = 'root'
        self.password = '123456'
        self.database = 'joy_rent'
        self.charset = 'utf8mb4'

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, config=None):
        self.config = config or DatabaseConfig()
        
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                charset=self.config.charset,
                autocommit=True
            )
            yield connection
        except Exception as e:
            logger.error(f"数据库连接错误: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("数据库连接测试成功")
                return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def get_user_by_phone(self, phone):
        """根据手机号获取用户信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                sql = """
                SELECT u.*, 
                       CASE WHEN uf.user_id IS NOT NULL THEN 1 ELSE 0 END as face_enabled
                FROM users u 
                LEFT JOIN user_face uf ON u.id = uf.user_id
                WHERE u.phone = %s
                """
                cursor.execute(sql, (phone,))
                user = cursor.fetchone()
                return user
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            return None
    
    def get_user_by_username(self, username):
        """根据用户名获取用户信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                sql = """
                SELECT u.*, 
                       CASE WHEN uf.user_id IS NOT NULL THEN 1 ELSE 0 END as face_enabled
                FROM users u 
                LEFT JOIN user_face uf ON u.id = uf.user_id
                WHERE u.username = %s
                """
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                return user
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """根据用户ID获取用户信息"""
        try:
            # 如果 user_id 是 UUID 字符串（非数字），返回一个模拟用户对象或者处理逻辑
            if isinstance(user_id, str) and not user_id.isdigit():
                return {
                    'id': user_id, 
                    'username': user_id, # 直接使用 UUID 作为 username
                    'nickname': '人脸注册用户',
                    'face_enabled': 0
                }

            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                sql = """
                SELECT u.*, 
                       CASE WHEN uf.user_id IS NOT NULL THEN 1 ELSE 0 END as face_enabled
                FROM users u 
                LEFT JOIN user_face uf ON u.id = uf.user_id
                WHERE u.id = %s
                """
                cursor.execute(sql, (user_id,))
                user = cursor.fetchone()
                return user
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            return None
    
    def save_user_face_embedding(self, user_id, face_embedding, img_url=None):
        """保存用户人脸特征向量 (支持 face_id 模式)"""
        try:
            # 将numpy数组转换为JSON字符串
            if isinstance(face_embedding, np.ndarray):
                face_embedding_json = json.dumps(face_embedding.tolist())
            else:
                face_embedding_json = json.dumps(face_embedding)
            
            # 判断 user_id 是否为真实的数字 ID
            is_numeric_id = isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit())

            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if is_numeric_id:
                    # 传统的 numeric ID 逻辑
                    check_sql = "SELECT user_id FROM user_face WHERE user_id = %s"
                    cursor.execute(check_sql, (user_id,))
                    existing_record = cursor.fetchone()
                    
                    if existing_record:
                        sql = "UPDATE user_face SET face_encoding = %s WHERE user_id = %s"
                        cursor.execute(sql, (face_embedding_json, user_id))
                    else:
                        sql = "INSERT INTO user_face (user_id, face_encoding) VALUES (%s, %s)"
                        cursor.execute(sql, (user_id, face_embedding_json))
                else:
                    # UUID (face_id) 模式逻辑
                    # 这种情况下，Java 会负责在 user_face 表中维护关联关系
                    # Python 端只需要确保 face_encoding 被存入即可（如果需要的话）
                    # 或者我们可以只进行文件存储，数据库存储交给 Java
                    logger.info(f"UUID 模式注册，跳过数据库更新，由 Java 端处理持久化: {user_id}")
                    return True
                
                return True
        except Exception as e:
            logger.error(f"保存人脸特征失败: {e}")
            return False
    
    def get_all_face_users(self):
        """获取所有启用人脸识别的用户 (优先读取 face_id 作为标识)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                # 修改查询语句，读取 face_id 和 face_encoding
                # 如果 face_id 为空，回退使用 username (为了兼容旧数据)
                sql = """
                SELECT u.id, u.username, u.phone, u.nickname, uf.face_encoding, uf.face_id
                FROM users u
                INNER JOIN user_face uf ON u.id = uf.user_id
                WHERE uf.face_encoding IS NOT NULL AND u.status = 1
                """
                cursor.execute(sql)
                users = cursor.fetchall()
                
                # 将标识符注入到 username 字段中，供识别服务使用
                for user in users:
                    if user.get('face_id'):
                        user['username'] = user['face_id']
                
                # 将JSON字符串转换回numpy数组
                for user in users:
                    if user['face_encoding']:
                        try:
                            face_data = json.loads(user['face_encoding'])
                            user['face_embedding'] = np.array(face_data)
                        except Exception as e:
                            logger.warning(f"用户 {user['username']} 的人脸数据格式错误: {e}")
                            logger.warning(f"错误数据片段: {str(user['face_encoding'])[:200]}")
                            
                            # 尝试修复数据
                            try:
                                # 情况1: 标准JSON但有额外数据 (如重复追加)
                                if "Extra data" in str(e) and user['face_encoding'].strip().startswith('['):
                                    end_idx = user['face_encoding'].find(']')
                                    if end_idx != -1:
                                        fixed_json = user['face_encoding'][:end_idx+1]
                                        face_data = json.loads(fixed_json)
                                        if isinstance(face_data, list) and len(face_data) > 100:
                                            user['face_embedding'] = np.array(face_data)
                                            logger.info(f"已自动修复用户 {user['username']} 的人脸数据 (截断修复)")
                                            continue
                                
                                # 情况2: 纯逗号分隔的字符串 (无方括号)
                                if ',' in user['face_encoding'] and not user['face_encoding'].strip().startswith('['):
                                    # 尝试按逗号分割并转换为浮点数
                                    face_data = [float(x.strip()) for x in user['face_encoding'].split(',') if x.strip()]
                                    if len(face_data) > 100:
                                        user['face_embedding'] = np.array(face_data)
                                        logger.info(f"已自动修复用户 {user['username']} 的人脸数据 (CSV格式)")
                                        continue
                            except Exception as fix_error:
                                logger.warning(f"尝试修复数据失败: {fix_error}")
                                
                            user['face_embedding'] = None
                
                return users
        except Exception as e:
            logger.error(f"获取人脸用户失败: {e}")
            return []
    
    def disable_user_face(self, user_id):
        """禁用用户人脸识别(删除人脸数据)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                sql = "DELETE FROM user_face WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                
                if cursor.rowcount > 0:
                    logger.info(f"用户 {user_id} 人脸识别已禁用")
                    return True
                else:
                    logger.warning(f"用户 {user_id} 不存在人脸数据")
                    return False
        except Exception as e:
            logger.error(f"禁用人脸识别失败: {e}")
            return False
    
    def verify_password(self, user_id, password_hash):
        """验证用户密码(MD5)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT id FROM users WHERE id = %s AND password = %s"
                cursor.execute(sql, (user_id, password_hash))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"验证密码失败: {e}")
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()

if __name__ == "__main__":
    # 测试数据库连接
    print("测试数据库连接...")
    if db_manager.test_connection():
        print("✅ 数据库连接成功")
        
        # 测试获取用户
        users = db_manager.get_all_face_users()
        print(f"📊 当前启用人脸识别的用户数量: {len(users)}")
        
    else:
        print("❌ 数据库连接失败")