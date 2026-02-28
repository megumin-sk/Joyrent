import psycopg2
from config import Config

def init_db():
    # 先连接默认数据库 postgres，用来创建用户指定的数据库
    conn = psycopg2.connect(
        dbname="postgres",
        user="root",
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # 尝试创建数据库（如果不存在）
    try:
        cur.execute(f"CREATE DATABASE {Config.DB_NAME}")
        print(f"Database {Config.DB_NAME} created.")
    except Exception as e:
        print(f"Database already exists or error: {e}")
    finally:
        cur.close()
        conn.close()

    # 连接到业务数据库进行初始化
    conn = psycopg2.connect(
        dbname=Config.DB_NAME,
        user="root",
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )
    cur = conn.cursor()
    try:
        # 启用扩展
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # 创建表
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
        print("Table 'documents' created successfully with dimension", Config.EMBEDDING_DIMENSION)
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_db()
