import psycopg2
from pgvector.psycopg2 import register_vector
from src.config import Config

def get_db_connection():
    """获取数据库连接"""
    conn = psycopg2.connect(
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )
    # 注册 pgvector 扩展，以便处理向量数据
    register_vector(conn)
    return conn

import mysql.connector

def get_mysql_connection():
    """获取 MySQL 业务数据库连接"""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="joy_rent",
        port=3306
    )
    return conn

def get_games_stock(game_ids):
    """批量从 MySQL 获取游戏库存信息"""
    if not game_ids:
        return {}
    
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    
    format_strings = ','.join(['%s'] * len(game_ids))
    sql = f"SELECT id, title, available_stock FROM games WHERE id IN ({format_strings})"
    
    print(f"====== [MySQL DEBUG] Executing: {sql} | Params: {game_ids} ======")
    cursor.execute(sql, tuple(game_ids))
    
    results = cursor.fetchall()
    conn.close()
    
    # 转为字典 {id: {'title': ..., 'stock': ...}}
    return {row['id']: row for row in results}

def init_db():
    """初始化数据库表"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 启用 vector 插件
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # cur.execute("DROP TABLE IF EXISTS documents")
        
        # 创建向量表
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                game_id INTEGER,
                category VARCHAR(100),
                content TEXT,
                embedding vector({Config.EMBEDDING_DIMENSION})
            )
        """)
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
