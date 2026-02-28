# AgentState 设计文档

## 🎯 核心设计理念

`AgentState` 是 LangGraph 流程中的"数据总线"，所有节点通过读取和修改这个状态来协同工作。

## 📊 状态字段分类

### 1️⃣ **对话历史** (messages)
```python
messages: Annotated[Sequence[BaseMessage], add_messages]
```

**作用**：存储完整的对话历史  
**特殊注解**：`add_messages` 让 LangGraph 自动追加新消息，不需要手动管理  
**示例**：
```python
[
    HumanMessage(content="塞尔达好玩吗？"),
    AIMessage(content="我帮您查一下..."),
    HumanMessage(content="还有库存吗？")
]
```

---

### 2️⃣ **意图识别** (intent + intent_confidence)
```python
intent: Optional[IntentType]  # "clarify" | "rule" | "game" | "order"
intent_confidence: float      # 0.0 - 1.0
```

**作用**：记录用户意图和置信度  
**流程**：`intent` 节点识别 → 路由节点根据 `intent` 分发  
**示例**：
```python
state["intent"] = "game"
state["intent_confidence"] = 0.95
```

---

### 3️⃣ **用户信息** (user_id + is_authenticated)
```python
user_id: Optional[str]
is_authenticated: bool
```

**作用**：权限校验（订单查询需要登录）  
**流程**：
```
订单查询 → 检查 is_authenticated
    ├─ True  → 查询订单
    └─ False → 提示登录
```

---

### 4️⃣ **上下文数据** (context)
```python
context: dict[str, Any]
```

**作用**：灵活存储中间结果  
**常见字段**：
```python
context = {
    "game_name": "塞尔达传说",      # 提取的游戏名
    "order_id": "ORD123456",       # 提取的订单号
    "search_query": "退款流程",    # 检索查询
}
```

---

### 5️⃣ **检索/查询结果**
```python
retrieved_rules: Optional[list[dict]]  # 规则检索结果
game_info: Optional[dict]              # RAWG 游戏信息
inventory_info: Optional[dict]         # 本地库存
order_info: Optional[dict]             # 订单信息
```

**作用**：存储各个工具的查询结果  
**示例**：
```python
# 规则检索
state["retrieved_rules"] = [
    {"content": "退款需在 7 天内...", "score": 0.95},
    {"content": "运费由买家承担...", "score": 0.87}
]

# 游戏信息
state["game_info"] = {
    "name": "The Legend of Zelda",
    "rating": 4.5,
    "released": "2017-03-03"
}

# 库存信息
state["inventory_info"] = {
    "game_id": 123,
    "stock": 5,
    "price": 30
}
```

---

### 6️⃣ **流程控制**
```python
clarify_count: int              # 澄清重试次数
route_status: RouteStatus       # 路由状态
error_message: Optional[str]    # 错误信息
```

**作用**：控制流程执行和异常处理  
**示例**：
```python
# 澄清循环控制
if state["clarify_count"] >= 3:
    return "抱歉，我还是没理解您的问题..."

# 降级处理
if rawg_api_failed:
    state["route_status"] = "degraded"
    state["error_message"] = "RAWG API 超时"
```

---

### 7️⃣ **最终回答** (final_answer)
```python
final_answer: Optional[str]
```

**作用**：存储大模型生成的最终回答  
**流程**：answer 节点生成 → 返回给用户

---

### 8️⃣ **调试信息** (debug_info)
```python
debug_info: dict[str, Any]
```

**作用**：记录调试信息（生产环境可选）  
**示例**：
```python
debug_info = {
    "intent_model_response": "game",
    "retrieval_time_ms": 45,
    "rawg_api_time_ms": 320,
    "total_tokens": 1250
}
```

---

## 🔄 状态流转示例

### 场景：用户问"塞尔达好玩吗？"

```python
# 1. 初始状态
state = create_initial_state("塞尔达好玩吗？")
# {
#     "messages": [HumanMessage("塞尔达好玩吗？")],
#     "intent": None,
#     "intent_confidence": 0.0,
#     ...
# }

# 2. 意图识别节点
state["intent"] = "game"
state["intent_confidence"] = 0.95
state["context"]["game_name"] = "塞尔达传说"

# 3. RAWG 查询节点
state["game_info"] = {
    "name": "The Legend of Zelda: Breath of the Wild",
    "rating": 4.5,
    "metacritic": 97
}
state["route_status"] = "success"

# 4. 库存查询节点
state["inventory_info"] = {
    "stock": 5,
    "price": 30
}

# 5. 回答生成节点
state["final_answer"] = "《塞尔达传说：旷野之息》是一款超棒的游戏！..."
state["messages"].append(AIMessage(state["final_answer"]))
```

---

## 🛠️ 辅助函数

### `create_initial_state()`
快速创建初始状态，避免手动初始化所有字段。

```python
state = create_initial_state("塞尔达好玩吗？", user_id="user_123")
```

### `should_clarify()`
判断是否需要继续澄清（防止无限循环）。

```python
if should_clarify(state):
    return "clarify_node"
else:
    return "fallback_node"
```

### `is_route_successful()`
判断路由是否成功执行。

```python
if is_route_successful(state):
    return "answer_node"
else:
    return "error_handler_node"
```

### `get_last_user_message()`
获取最后一条用户消息（用于重新分析意图）。

```python
user_input = get_last_user_message(state)
```

---

## 🎨 设计亮点

### 1. **类型安全**
使用 `TypedDict` 和 `Literal` 确保类型正确：
```python
IntentType = Literal["clarify", "rule", "game", "order"]
```

### 2. **自动消息管理**
`add_messages` 注解自动追加消息，无需手动管理：
```python
messages: Annotated[Sequence[BaseMessage], add_messages]
```

### 3. **灵活的上下文**
`context` 字典可以存储任意中间结果，适应不同场景。

### 4. **容错设计**
`route_status` 支持降级状态（`degraded`），允许部分成功。

### 5. **可观测性**
`debug_info` 记录关键指标，便于性能分析和问题排查。

---

## 📝 使用建议

### ✅ **推荐做法**
```python
# 1. 使用辅助函数创建状态
state = create_initial_state(user_input, user_id)

# 2. 在节点中更新状态
def intent_node(state: AgentState) -> AgentState:
    state["intent"] = classify_intent(state)
    return state

# 3. 使用辅助函数判断流程
if should_clarify(state):
    return "clarify"
```

### ❌ **避免的做法**
```python
# 1. 不要直接修改 messages（使用 add_messages）
state["messages"] = [...]  # ❌

# 2. 不要忘记更新 route_status
# 查询成功后应该设置 state["route_status"] = "success"

# 3. 不要在 context 中存储大对象
state["context"]["huge_data"] = [...]  # ❌ 会占用大量内存
```

---

## 🚀 下一步

现在 `AgentState` 已经定义好了，接下来可以：

1. **实现 graph.py**：构建 LangGraph 流程
2. **实现各个节点**：
   - `nodes/intent.py`：意图识别
   - `nodes/retrieve.py`：规则检索
   - `nodes/answer.py`：回答生成
3. **编写单元测试**：验证状态流转逻辑

---

## 🔍 常见问题

### Q: 为什么要用 TypedDict 而不是 dataclass？
A: LangGraph 要求使用 `TypedDict`，因为它需要序列化状态（用于持久化和分布式执行）。

### Q: context 和 debug_info 有什么区别？
A: `context` 存储业务相关的中间结果，`debug_info` 存储技术指标（可选）。

### Q: 为什么 messages 用 Sequence 而不是 list？
A: `Sequence` 是不可变的，配合 `add_messages` 注解，LangGraph 会自动管理消息追加。

### Q: route_status 的 degraded 是什么意思？
A: 部分成功。比如 RAWG API 失败，但本地库存查询成功，可以返回部分信息。
