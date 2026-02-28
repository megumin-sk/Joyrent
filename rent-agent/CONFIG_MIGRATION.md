# 配置迁移说明

## 📋 迁移概览

从 `rag_llm_engine` 迁移到 `rent-agent`，主要变化：

### ✅ 已完成的迁移

1. **配置文件结构**
   - ✅ `config.py`：从单模型升级到双模型架构
   - ✅ `.env.example`：添加新的环境变量配置项
   - ✅ `pyproject.toml`：添加完整的依赖列表

2. **核心配置项**
   - ✅ 双模型架构：`INTENT_MODEL` (tongyi-xiaomi-analysis-flash) + `ANSWER_MODEL` (qwen3.5-plus)
   - ✅ 数据库连接：PostgreSQL (向量检索) + MySQL (业务数据)
   - ✅ IGDB API：游戏信息查询（更专业的游戏数据库）
   - ✅ Redis 缓存：可选的性能优化

3. **系统提示词**
   - ✅ `INTENT_SYSTEM_PROMPT`：意图分类提示词
   - ✅ `ANSWER_SYSTEM_PROMPT`：回答生成提示词
   - ✅ `CLARIFY_SYSTEM_PROMPT`：澄清问题提示词

---

## 🔧 配置对比

### rag_llm_engine（旧）
```python
LLM_MODEL = "qwen3.5-plus"  # 单一模型
EMBEDDING_MODEL = "multimodal-embedding-v1"
TOP_K = 3
MEMORY_WINDOW_SIZE = 10
```

### rent-agent（新）
```python
# 双模型架构（成本优化）
INTENT_MODEL = "tongyi-xiaomi-analysis-flash"          # 意图识别（便宜）
ANSWER_MODEL = "qwen3.5-plus"           # 最终回答（性能强）
EMBEDDING_MODEL = "text-embedding-v3"

# 流程控制
TOP_K = 3
MAX_CLARIFY_RETRIES = 3              # 新增：澄清循环限制
MEMORY_WINDOW_SIZE = 10

# 缓存配置（新增）
CACHE_TTL_GAME_INFO = 86400          # 游戏信息缓存 24h
CACHE_TTL_RULES = 3600               # 规则缓存 1h
```

---

## 📦 依赖变化

### 新增依赖
```toml
# LangGraph 核心
langgraph>=0.2.0
langchain>=0.3.0

# 数据库
pgvector>=0.3.0        # PostgreSQL 向量扩展
pymysql>=1.1.0         # MySQL 驱动

# 缓存
redis>=5.0.0

# HTTP 客户端
httpx>=0.27.0          # RAWG API 调用

# 可观测性
prometheus-client>=0.21.0
```

---

## 🚀 快速开始

### 1. 安装依赖
```bash
cd d:\workspace\JoyRent\SwitchRent\rent-agent
pip install -e .
```

### 2. 配置环境变量
```bash
# 复制 .env.example 到 .env
cp .env.example .env

# 编辑 .env 文件，填入真实的 API Key
# - DASHSCOPE_API_KEY
# - RAWG_API_KEY
# - 数据库密码
```

### 3. 验证配置
```python
from rent_agent.config import config

# 检查配置是否正确加载
print(f"意图模型: {config.INTENT_MODEL}")
print(f"回答模型: {config.ANSWER_MODEL}")
print(f"PostgreSQL: {config.DATABASE_URL}")
print(f"MySQL: {config.MYSQL_URL}")
```

---

## 🎯 核心设计理念

### 双模型架构的优势

```
┌─────────────────────────────────────────────────┐
│  用户输入                                        │
│      ↓                                          │
│  意图识别（tongyi-xiaomi-analysis-flash）                         │
│      ├─ 成本：¥0.0008/1K tokens                │
│      ├─ 速度：快                                │
│      └─ 任务：简单分类（clarify/rule/game/order）│
│      ↓                                          │
│  路由到不同分支                                  │
│      ↓                                          │
│  最终回答（qwen3.5-plus）                          │
│      ├─ 成本：¥0.004/1K tokens                 │
│      ├─ 速度：中等                              │
│      └─ 任务：复杂推理 + 自然回答               │
└─────────────────────────────────────────────────┘

总成本：约 ¥0.005/次对话（比单一大模型节省 60%）
```

### 容错与降级

```python
# 每个外部依赖都有 fallback
RAWG 查询失败 → 降级回答（只返回本地库存）
库存查询失败 → 部分信息回答（只返回游戏信息）
订单查询失败 → 友好提示（服务暂时不可用）
```

---

## 📊 监控指标建议

在生产环境中，建议监控以下指标：

```python
# 意图识别准确率
intent_accuracy = correct_intents / total_intents

# 各路由分支流量占比
route_distribution = {
    "clarify": 15%,
    "rule": 25%,
    "game": 45%,
    "order": 15%
}

# 外部服务成功率
rawg_success_rate = successful_calls / total_calls
inventory_success_rate = ...
order_success_rate = ...

# 成本统计
daily_cost = intent_calls * 0.0008 + answer_calls * 0.004
```

---

## 🔐 安全注意事项

1. **API Key 管理**
   - ❌ 不要将 `.env` 文件提交到 Git
   - ✅ 使用环境变量或密钥管理服务
   - ✅ 定期轮换 API Key

2. **数据库连接**
   - ✅ 使用连接池（SQLAlchemy 自动管理）
   - ✅ 设置合理的超时时间
   - ✅ 生产环境使用 SSL 连接

3. **用户隐私**
   - ✅ 订单查询前验证用户身份
   - ✅ 不在日志中记录敏感信息
   - ✅ 遵守数据保留政策

---

## 📝 下一步

- [ ] 实现 `state.py`（AgentState 定义）
- [ ] 实现 `graph.py`（LangGraph 流程编排）
- [ ] 实现各个节点（intent、retrieve、answer 等）
- [ ] 编写单元测试
- [ ] 部署到生产环境

---

## 🆘 常见问题

### Q: 为什么要用两个模型？
A: 意图识别是简单的分类任务，用便宜的 tongyi-xiaomi-analysis-flash 就够了。只在最终回答时用 qwen3.5-plus，可以节省 60% 成本。

### Q: 可以只用一个模型吗？
A: 可以，设置 `INTENT_MODEL=qwen3.5-plus` 即可。但成本会显著增加。

### Q: Redis 是必须的吗？
A: 不是必须的，但强烈推荐。缓存可以显著降低 RAWG API 调用次数和响应时间。

### Q: 如何切换到其他 LLM？
A: 修改 `config.py` 中的模型名称即可，只要兼容 OpenAI SDK 格式。
