"""
rent-agent LangGraph 状态定义

AgentState 是整个对话流程中传递的核心数据结构，包含：
- 对话历史
- 意图识别结果
- 路由信息
- 检索/查询结果
- 用户信息
- 流程控制标志
"""
from typing import TypedDict, Annotated, Sequence, Optional, Literal, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


# 意图类型定义
IntentType = Literal["clarify", "rule", "game", "order"]

# 路由状态定义
RouteStatus = Literal["pending", "success", "failed", "degraded"]


class AgentState(TypedDict):
    """
    rent-agent 的核心状态类
    
    这个状态会在整个 LangGraph 流程中传递和更新。
    每个节点可以读取和修改这个状态。
    """
    
    # ==================== 对话历史 ====================
    messages: Annotated[Sequence[BaseMessage], add_messages]
    """
    对话消息历史（自动累积）
    使用 add_messages 注解，LangGraph 会自动追加新消息
    """
    
    # ==================== 意图识别 ====================
    intent: Optional[IntentType]
    """
    用户意图类型：
    - clarify: 需要澄清
    - rule: 平台规则查询
    - game: 游戏信息查询
    - order: 订单查询
    """
    
    intent_confidence: float
    """意图识别的置信度（0-1）"""
    
    # ==================== 用户信息 ====================
    user_id: Optional[str]
    """用户 ID（用于订单查询权限校验）"""
    
    is_authenticated: bool
    """用户是否已登录"""
    
    # ==================== 上下文数据 ====================
    context: dict[str, Any]
    """
    存储中间结果和上下文信息，例如：
    - game_name: 用户询问的游戏名称
    - order_id: 订单号
    - search_query: 检索查询
    - retrieved_docs: 检索到的文档
    - game_info: RAWG API 返回的游戏信息
    - inventory_data: 库存查询结果
    - order_data: 订单查询结果
    """
    
    # ==================== 检索结果 ====================
    retrieved_rules: Optional[list[dict]]
    """
    规则检索结果（RAG）
    格式：[{"content": "规则内容", "score": 0.95}, ...]
    """
    
    game_info: Optional[dict]
    """
    IGDB API 返回的游戏信息
    格式：{"name": "塞尔达传说", "rating": 4.5, "summary": "...", ...}
    """
    
    inventory_info: Optional[dict]
    """
    本地库存查询结果
    格式：{"game_id": 123, "stock": 5, "price": 30, ...}
    """
    
    order_info: Optional[dict]
    """
    订单查询结果
    格式：{"order_id": "xxx", "status": "已发货", "tracking": "...", ...}
    """
    
    # ==================== 流程控制 ====================
    clarify_count: int
    """澄清问题的重试次数（防止无限循环）"""
    
    route_status: RouteStatus
    """
    当前路由的执行状态：
    - pending: 待执行
    - success: 成功
    - failed: 失败
    - degraded: 降级（部分成功）
    """
    
    error_message: Optional[str]
    """错误信息（如果有）"""
    
    # ==================== 最终回答 ====================
    final_answer: Optional[str]
    """大模型生成的最终回答"""
    
    # ==================== 调试信息 ====================
    debug_info: dict[str, Any]
    """
    调试信息（可选），例如：
    - intent_model_response: 意图识别模型的原始响应
    - retrieval_scores: 检索分数
    - api_call_times: API 调用耗时
    """


def create_initial_state(user_input: str, user_id: Optional[str] = None) -> AgentState:
    """
    创建初始状态
    
    Args:
        user_input: 用户输入
        user_id: 用户 ID（可选）
    
    Returns:
        初始化的 AgentState
    """
    from langchain_core.messages import HumanMessage
    
    return AgentState(
        messages=[HumanMessage(content=user_input)],
        intent=None,
        intent_confidence=0.0,
        user_id=user_id,
        is_authenticated=user_id is not None,
        context={},
        retrieved_rules=None,
        game_info=None,
        inventory_info=None,
        order_info=None,
        clarify_count=0,
        route_status="pending",
        error_message=None,
        final_answer=None,
        debug_info={},
    )


def should_clarify(state: AgentState) -> bool:
    """
    判断是否需要澄清问题
    
    Args:
        state: 当前状态
    
    Returns:
        是否需要澄清
    """
    from rent_agent.config import config
    
    return (
        state["intent"] == "clarify"
        and state["clarify_count"] < config.MAX_CLARIFY_RETRIES
    )


def is_route_successful(state: AgentState) -> bool:
    """
    判断路由是否成功执行
    
    Args:
        state: 当前状态
    
    Returns:
        路由是否成功
    """
    return state["route_status"] in ["success", "degraded"]


def get_last_user_message(state: AgentState) -> str:
    """
    获取最后一条用户消息
    
    Args:
        state: 当前状态
    
    Returns:
        最后一条用户消息内容
    """
    from langchain_core.messages import HumanMessage
    
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return message.content
    return ""


# ==================== 类型导出 ====================
__all__ = [
    "AgentState",
    "IntentType",
    "RouteStatus",
    "create_initial_state",
    "should_clarify",
    "is_route_successful",
    "get_last_user_message",
]

