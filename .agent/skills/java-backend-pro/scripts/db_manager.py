#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库表结构管理工具
功能：查询、修改表结构，支持字段和索引的增删改查
作者：JoyRent Team
版本：1.0.0
"""

import pymysql
import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Optional

# 数据库连接配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "joy_rent",
    "charset": "utf8mb4"
}

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, config: Dict = None):
        """初始化数据库连接"""
        self.config = config or DB_CONFIG
        self.conn = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = pymysql.connect(**self.config)
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}", file=sys.stderr)
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def execute(self, sql: str, params: tuple = None, fetch: bool = False):
        """执行SQL语句"""
        try:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                if fetch:
                    return cursor.fetchall()
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"❌ SQL执行失败: {e}", file=sys.stderr)
            print(f"SQL: {sql}", file=sys.stderr)
            return None
    
    # ==================== 查询功能 ====================
    
    def list_tables(self) -> List[str]:
        """列出所有表"""
        result = self.execute("SHOW TABLES", fetch=True)
        if result:
            return [list(row.values())[0] for row in result]
        return []
    
    def get_table_structure(self, table_name: str) -> Dict:
        """获取表结构详情"""
        # 获取表注释
        comment_sql = f"""
            SELECT TABLE_COMMENT 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = '{self.config['database']}' 
            AND TABLE_NAME = '{table_name}'
        """
        comment_result = self.execute(comment_sql, fetch=True)
        table_comment = comment_result[0]['TABLE_COMMENT'] if comment_result else ""
        
        # 获取列信息
        columns = self.execute(f"SHOW FULL COLUMNS FROM `{table_name}`", fetch=True)
        
        # 获取索引信息
        indexes = self.execute(f"SHOW INDEX FROM `{table_name}`", fetch=True)
        
        return {
            "name": table_name,
            "comment": table_comment,
            "columns": columns or [],
            "indexes": indexes or []
        }
    
    def print_table_structure(self, table_name: str):
        """打印表结构（Markdown格式）"""
        structure = self.get_table_structure(table_name)
        
        print(f"\n## 📋 表: `{structure['name']}`")
        if structure['comment']:
            print(f"**说明**: {structure['comment']}\n")
        
        print("### 字段列表")
        print("| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |")
        print("|--------|------|----------|-----|--------|------|------|")
        for col in structure['columns']:
            default_val = col['Default'] if col['Default'] is not None else "NULL"
            print(f"| {col['Field']} | {col['Type']} | {col['Null']} | {col['Key']} | {default_val} | {col['Extra']} | {col['Comment']} |")
        
        print("\n### 索引列表")
        print("| 索引名 | 列名 | 唯一性 | 类型 |")
        print("|--------|------|--------|------|")
        for idx in structure['indexes']:
            unique = "✅ 唯一" if not idx['Non_unique'] else "❌ 非唯一"
            print(f"| {idx['Key_name']} | {idx['Column_name']} | {unique} | {idx['Index_type']} |")
        print()
    
    # ==================== 字段操作 ====================
    
    def add_column(self, table_name: str, column_name: str, column_type: str, 
                   after: str = None, comment: str = "", default: str = None, 
                   nullable: bool = True):
        """添加字段"""
        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_type}"
        
        if not nullable:
            sql += " NOT NULL"
        
        if default is not None:
            sql += f" DEFAULT {default}"
        
        if comment:
            sql += f" COMMENT '{comment}'"
        
        if after:
            sql += f" AFTER `{after}`"
        
        print(f"🔧 执行SQL: {sql}")
        result = self.execute(sql)
        if result:
            print(f"✅ 字段 `{column_name}` 添加成功")
        return result
    
    def modify_column(self, table_name: str, column_name: str, new_type: str, 
                      comment: str = None, default: str = None, nullable: bool = True):
        """修改字段"""
        sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{column_name}` {new_type}"
        
        if not nullable:
            sql += " NOT NULL"
        
        if default is not None:
            sql += f" DEFAULT {default}"
        
        if comment:
            sql += f" COMMENT '{comment}'"
        
        print(f"🔧 执行SQL: {sql}")
        result = self.execute(sql)
        if result:
            print(f"✅ 字段 `{column_name}` 修改成功")
        return result
    
    def drop_column(self, table_name: str, column_name: str, confirm: bool = False):
        """删除字段"""
        if not confirm:
            print(f"⚠️  警告：即将删除表 `{table_name}` 的字段 `{column_name}`")
            response = input("确认删除？(yes/no): ")
            if response.lower() != 'yes':
                print("❌ 操作已取消")
                return False
        
        sql = f"ALTER TABLE `{table_name}` DROP COLUMN `{column_name}`"
        print(f"🔧 执行SQL: {sql}")
        result = self.execute(sql)
        if result:
            print(f"✅ 字段 `{column_name}` 删除成功")
        return result
    
    # ==================== 索引操作 ====================
    
    def add_index(self, table_name: str, index_name: str, columns: List[str], 
                  unique: bool = False, index_type: str = "BTREE"):
        """添加索引"""
        index_keyword = "UNIQUE INDEX" if unique else "INDEX"
        columns_str = ", ".join([f"`{col}`" for col in columns])
        
        sql = f"ALTER TABLE `{table_name}` ADD {index_keyword} `{index_name}` ({columns_str}) USING {index_type}"
        print(f"🔧 执行SQL: {sql}")
        result = self.execute(sql)
        if result:
            print(f"✅ 索引 `{index_name}` 添加成功")
        return result
    
    def drop_index(self, table_name: str, index_name: str, confirm: bool = False):
        """删除索引"""
        if not confirm:
            print(f"⚠️  警告：即将删除表 `{table_name}` 的索引 `{index_name}`")
            response = input("确认删除？(yes/no): ")
            if response.lower() != 'yes':
                print("❌ 操作已取消")
                return False
        
        sql = f"ALTER TABLE `{table_name}` DROP INDEX `{index_name}`"
        print(f"🔧 执行SQL: {sql}")
        result = self.execute(sql)
        if result:
            print(f"✅ 索引 `{index_name}` 删除成功")
        return result
    
    # ==================== 备份与恢复 ====================
    
    def backup_table(self, table_name: str, backup_name: str = None):
        """备份表"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{table_name}_backup_{timestamp}"
        
        sql = f"CREATE TABLE `{backup_name}` LIKE `{table_name}`"
        if self.execute(sql):
            sql = f"INSERT INTO `{backup_name}` SELECT * FROM `{table_name}`"
            if self.execute(sql):
                print(f"✅ 表 `{table_name}` 已备份为 `{backup_name}`")
                return backup_name
        return None
    
    # ==================== 自定义SQL ====================
    
    def execute_custom_sql(self, sql: str, confirm: bool = False):
        """执行自定义SQL"""
        if not confirm:
            print(f"⚠️  即将执行SQL:")
            print(f"   {sql}")
            response = input("确认执行？(yes/no): ")
            if response.lower() != 'yes':
                print("❌ 操作已取消")
                return False
        
        # 自动判断是否为查询语句
        is_select = sql.strip().upper().startswith("SELECT")
        result = self.execute(sql, fetch=is_select)
        
        if result is True:
            print(f"✅ SQL执行成功")
        elif isinstance(result, list):
            print(f"✅ 查询成功，共 {len(result)} 条记录:\n")
            if not result:
                print("（结果为空）")
            else:
                # 打印表头
                headers = result[0].keys()
                header_line = "| " + " | ".join(headers) + " |"
                sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
                print(header_line)
                print(sep_line)
                # 打印数据
                for row in result:
                    row_line = "| " + " | ".join([str(v) for v in row.values()]) + " |"
                    print(row_line)
            print()
        return result


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(description="JoyRent 数据库表结构管理工具")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 一键导出所有表结构（整合 db_inspector.py 功能）
    inspect_parser = subparsers.add_parser('inspect', help='导出所有表结构（Markdown格式）')
    inspect_parser.add_argument('--output', '-o', help='输出文件路径（默认输出到控制台）')
    
    # 列出所有表
    subparsers.add_parser('list', help='列出所有表')
    
    # 查看表结构
    show_parser = subparsers.add_parser('show', help='查看表结构')
    show_parser.add_argument('table', help='表名')
    
    # 添加字段
    add_col_parser = subparsers.add_parser('add-column', help='添加字段')
    add_col_parser.add_argument('table', help='表名')
    add_col_parser.add_argument('column', help='字段名')
    add_col_parser.add_argument('type', help='字段类型，如: VARCHAR(100)')
    add_col_parser.add_argument('--after', help='在哪个字段之后')
    add_col_parser.add_argument('--comment', default='', help='字段说明')
    add_col_parser.add_argument('--default', help='默认值')
    add_col_parser.add_argument('--not-null', action='store_true', help='不允许NULL')
    
    # 修改字段
    mod_col_parser = subparsers.add_parser('modify-column', help='修改字段')
    mod_col_parser.add_argument('table', help='表名')
    mod_col_parser.add_argument('column', help='字段名')
    mod_col_parser.add_argument('type', help='新字段类型')
    mod_col_parser.add_argument('--comment', help='字段说明')
    mod_col_parser.add_argument('--default', help='默认值')
    mod_col_parser.add_argument('--not-null', action='store_true', help='不允许NULL')
    
    # 删除字段
    drop_col_parser = subparsers.add_parser('drop-column', help='删除字段')
    drop_col_parser.add_argument('table', help='表名')
    drop_col_parser.add_argument('column', help='字段名')
    drop_col_parser.add_argument('--yes', action='store_true', help='跳过确认')
    
    # 添加索引
    add_idx_parser = subparsers.add_parser('add-index', help='添加索引')
    add_idx_parser.add_argument('table', help='表名')
    add_idx_parser.add_argument('index', help='索引名')
    add_idx_parser.add_argument('columns', nargs='+', help='列名（可多个）')
    add_idx_parser.add_argument('--unique', action='store_true', help='唯一索引')
    
    # 删除索引
    drop_idx_parser = subparsers.add_parser('drop-index', help='删除索引')
    drop_idx_parser.add_argument('table', help='表名')
    drop_idx_parser.add_argument('index', help='索引名')
    drop_idx_parser.add_argument('--yes', action='store_true', help='跳过确认')
    
    # 备份表
    backup_parser = subparsers.add_parser('backup', help='备份表')
    backup_parser.add_argument('table', help='表名')
    backup_parser.add_argument('--name', help='备份表名（可选）')
    
    # 执行自定义SQL
    sql_parser = subparsers.add_parser('sql', help='执行自定义SQL')
    sql_parser.add_argument('statement', help='SQL语句')
    sql_parser.add_argument('--yes', action='store_true', help='跳过确认')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建数据库管理器
    db = DatabaseManager()
    if not db.connect():
        sys.exit(1)
    
    try:
        # 执行对应命令
        if args.command == 'inspect':
            # 导出所有表结构
            tables = db.list_tables()
            output_lines = []
            output_lines.append(f"# Database Schema: {DB_CONFIG['database']}\n")
            output_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output_lines.append(f"**表数量**: {len(tables)}\n")
            output_lines.append("---\n")
            
            for table in tables:
                structure = db.get_table_structure(table)
                output_lines.append(f"\n## 📋 表: `{structure['name']}`\n")
                if structure['comment']:
                    output_lines.append(f"**说明**: {structure['comment']}\n")
                
                output_lines.append("\n### 字段列表\n")
                output_lines.append("| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |\n")
                output_lines.append("|--------|------|----------|-----|--------|------|------|\n")
                for col in structure['columns']:
                    default_val = col['Default'] if col['Default'] is not None else "NULL"
                    output_lines.append(f"| {col['Field']} | {col['Type']} | {col['Null']} | {col['Key']} | {default_val} | {col['Extra']} | {col['Comment']} |\n")
                
                output_lines.append("\n### 索引列表\n")
                output_lines.append("| 索引名 | 列名 | 唯一性 | 类型 |\n")
                output_lines.append("|--------|------|--------|------|\n")
                for idx in structure['indexes']:
                    unique = "✅ 唯一" if not idx['Non_unique'] else "❌ 非唯一"
                    output_lines.append(f"| {idx['Key_name']} | {idx['Column_name']} | {unique} | {idx['Index_type']} |\n")
                output_lines.append("\n---\n")
            
            # 输出到文件或控制台
            content = ''.join(output_lines)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 数据库结构已导出到: {args.output}")
            else:
                print(content)
        
        elif args.command == 'list':
            tables = db.list_tables()
            print(f"\n📚 数据库 `{DB_CONFIG['database']}` 中的表:")
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table}")
            print()
        
        elif args.command == 'show':
            db.print_table_structure(args.table)
        
        elif args.command == 'add-column':
            db.add_column(
                args.table, args.column, args.type,
                after=args.after, comment=args.comment,
                default=args.default, nullable=not args.not_null
            )
        
        elif args.command == 'modify-column':
            db.modify_column(
                args.table, args.column, args.type,
                comment=args.comment, default=args.default,
                nullable=not args.not_null
            )
        
        elif args.command == 'drop-column':
            db.drop_column(args.table, args.column, confirm=args.yes)
        
        elif args.command == 'add-index':
            db.add_index(args.table, args.index, args.columns, unique=args.unique)
        
        elif args.command == 'drop-index':
            db.drop_index(args.table, args.index, confirm=args.yes)
        
        elif args.command == 'backup':
            db.backup_table(args.table, backup_name=args.name)
        
        elif args.command == 'sql':
            db.execute_custom_sql(args.statement, confirm=args.yes)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
