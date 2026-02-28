# 数据库表结构管理工具使用指南

## 📖 简介

`db_manager.py` 是一个功能完整、复用性强的数据库表结构管理工具，支持：
- ✅ 查询表结构
- ✅ 添加/修改/删除字段
- ✅ 添加/删除索引
- ✅ 备份表
- ✅ 执行自定义SQL

## 🚀 快速开始

### 0. 一键导出所有表结构（推荐）
```bash
# 导出到文件
python .agent/skills/java-backend-pro/scripts/db_manager.py inspect -o db_schema.md

# 输出到控制台
python .agent/skills/java-backend-pro/scripts/db_manager.py inspect
```

### 1. 查看所有表
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py list
```

### 2. 查看单个表结构
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py show game_reviews
```

## 📋 字段操作

### 添加字段
```bash
# 基础用法
python .agent/skills/java-backend-pro/scripts/db_manager.py add-column \
  game_reviews \
  new_field \
  "VARCHAR(100)" \
  --comment "新字段说明"

# 完整参数
python .agent/skills/java-backend-pro/scripts/db_manager.py add-column \
  game_reviews \
  status \
  "TINYINT" \
  --after rating \
  --comment "状态字段" \
  --default 0 \
  --not-null
```

**参数说明**：
- `table`: 表名
- `column`: 字段名
- `type`: 字段类型（如 `VARCHAR(100)`, `INT`, `TINYINT`）
- `--after`: 在哪个字段之后插入（可选）
- `--comment`: 字段说明（可选）
- `--default`: 默认值（可选）
- `--not-null`: 不允许NULL（可选，默认允许NULL）

### 修改字段
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py modify-column \
  game_reviews \
  content \
  "TEXT" \
  --comment "评论内容（已扩容）"
```

### 删除字段
```bash
# 需要确认
python .agent/skills/java-backend-pro/scripts/db_manager.py drop-column \
  game_reviews \
  old_field

# 跳过确认（危险操作！）
python .agent/skills/java-backend-pro/scripts/db_manager.py drop-column \
  game_reviews \
  old_field \
  --yes
```

## 🔍 索引操作

### 添加普通索引
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py add-index \
  game_reviews \
  idx_created_at \
  created_at
```

### 添加唯一索引
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py add-index \
  users \
  uk_email \
  email \
  --unique
```

### 添加复合索引
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py add-index \
  game_reviews \
  idx_user_game \
  user_id game_id
```

### 删除索引
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py drop-index \
  game_reviews \
  idx_old_index \
  --yes
```

## 💾 备份表

### 自动命名备份
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py backup game_reviews
# 生成表名如: game_reviews_backup_20260123_211500
```

### 指定备份表名
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py backup \
  game_reviews \
  --name game_reviews_before_migration
```

## 🛠️ 执行自定义SQL

```bash
# 需要确认
python .agent/skills/java-backend-pro/scripts/db_manager.py sql \
  "UPDATE game_reviews SET is_hidden = 0 WHERE ai_judge = 0"

# 跳过确认
python .agent/skills/java-backend-pro/scripts/db_manager.py sql \
  "DELETE FROM game_reviews WHERE id = 999" \
  --yes
```

## 📚 常见使用场景

### 场景1：为 `game_reviews` 表添加"点赞数"字段
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py add-column \
  game_reviews \
  like_count \
  "INT" \
  --after content \
  --comment "点赞数" \
  --default 0 \
  --not-null
```

### 场景2：修改 `content` 字段长度
```bash
# 先备份
python .agent/skills/java-backend-pro/scripts/db_manager.py backup game_reviews

# 再修改
python .agent/skills/java-backend-pro/scripts/db_manager.py modify-column \
  game_reviews \
  content \
  "VARCHAR(2000)" \
  --comment "评价内容（已扩容至2000字符）"
```

### 场景3：为高频查询添加索引
```bash
# 查看当前索引
python .agent/skills/java-backend-pro/scripts/db_manager.py show game_reviews

# 添加索引
python .agent/skills/java-backend-pro/scripts/db_manager.py add-index \
  game_reviews \
  idx_game_created \
  game_id created_at
```

### 场景4：清理测试数据
```bash
python .agent/skills/java-backend-pro/scripts/db_manager.py sql \
  "DELETE FROM game_reviews WHERE user_id = 999" \
  --yes
```

## ⚙️ 配置数据库连接

编辑脚本开头的 `DB_CONFIG` 字典：

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "joy_rent",
    "charset": "utf8mb4"
}
```

## ⚠️ 安全提示

1. **生产环境操作前务必备份**
   ```bash
   python .agent/skills/java-backend-pro/scripts/db_manager.py backup <table_name>
   ```

2. **删除操作会要求确认**，除非使用 `--yes` 参数

3. **修改字段类型可能导致数据丢失**，请先评估影响

4. **索引操作会锁表**，大表操作请在低峰期进行

## 🔧 依赖安装

```bash
pip install pymysql
```

## 📝 输出示例

### 查看表结构输出
```
## 📋 表: `game_reviews`
**说明**: 游戏评价表(含AI分析)

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| user_id | bigint | NO |  | NULL |  | 评价人ID |
| game_id | bigint | NO |  | NULL |  | 被评价的游戏ID |
| order_id | bigint | NO | MUL | NULL |  | 关联订单ID |
| rating | tinyint | NO |  | 5 |  | 用户打分: 1-5 星 |
...

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| uk_order_game | order_id | ✅ 唯一 | BTREE |
| idx_game_id | game_id | ❌ 非唯一 | BTREE |
```

## 🎯 最佳实践

1. **结构先行**：修改代码前先查看表结构
   ```bash
   python .agent/skills/java-backend-pro/scripts/db_manager.py show <table>
   ```

2. **备份优先**：重要操作前先备份
   ```bash
   python .agent/skills/java-backend-pro/scripts/db_manager.py backup <table>
   ```

3. **索引优化**：根据查询频率添加索引
   - 单列索引：高频WHERE条件
   - 复合索引：多字段联合查询
   - 唯一索引：业务唯一性约束

4. **字段规范**：
   - 使用有意义的字段名（小写+下划线）
   - 添加清晰的 `comment`
   - 合理设置 `default` 和 `NOT NULL`

---

**作者**: JoyRent Team  
**版本**: 1.0.0  
**最后更新**: 2026-01-23
