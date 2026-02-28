import pymysql
import json
import os
import sys

# 数据库连接配置 (默认使用用户提供的配置)
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "joy_rent",
    "charset": "utf8mb4"
}

def get_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        return None

def fetch_table_structures():
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取所有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            db_schema = {}
            
            for table_dict in tables:
                table_name = list(table_dict.values())[0]
                
                # 获取表注释
                cursor.execute(f"""
                    SELECT TABLE_COMMENT 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}' 
                    AND TABLE_NAME = '{table_name}'
                """)
                row = cursor.fetchone()
                table_comment = row['TABLE_COMMENT'] if row else ""
                
                # 获取列信息
                cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
                columns = cursor.fetchall()
                
                # 获取索引信息
                cursor.execute(f"SHOW INDEX FROM `{table_name}`")
                indexes = cursor.fetchall()
                
                db_schema[table_name] = {
                    "comment": table_comment,
                    "columns": [
                        {
                            "field": col['Field'],
                            "type": col['Type'],
                            "null": col['Null'],
                            "key": col['Key'],
                            "default": col['Default'],
                            "extra": col['Extra'],
                            "comment": col['Comment']
                        } for col in columns
                    ],
                    "indexes": [
                        {
                            "name": idx['Key_name'],
                            "column": idx['Column_name'],
                            "unique": not idx['Non_unique']
                        } for idx in indexes
                    ]
                }
            
            return db_schema
    except Exception as e:
        print(f"Error fetching schema: {e}", file=sys.stderr)
        return None
    finally:
        conn.close()

def print_markdown_schema(schema):
    if not schema:
        print("No schema found or error occurred.")
        return

    print(f"# Database Schema: {DB_CONFIG['database']}\n")
    
    for table_name, detail in schema.items():
        print(f"## Table: `{table_name}`")
        if detail['comment']:
            print(f"**Comment**: {detail['comment']}\n")
        else:
            print("\n")
            
        print("| Field | Type | Null | Key | Default | Extra | Comment |")
        print("|-------|------|------|-----|---------|-------|---------|")
        for col in detail['columns']:
            # 处理默认值为 None 的显示
            default_val = col['default'] if col['default'] is not None else "NULL"
            print(f"| {col['field']} | {col['type']} | {col['null']} | {col['key']} | {default_val} | {col['extra']} | {col['comment']} |")
        
        print("\n### Indexes")
        print("| Index Name | Column | Unique |")
        print("|------------|--------|--------|")
        for idx in detail['indexes']:
            print(f"| {idx['name']} | {idx['column']} | {idx['unique']} |")
        print("\n---\n")

if __name__ == "__main__":
    schema = fetch_table_structures()
    if schema:
        print_markdown_schema(schema)
    else:
        sys.exit(1)
