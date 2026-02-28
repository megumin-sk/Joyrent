"""
JoyRent Agent — LangGraph 工作流编排

核心流程：
START → intent_node → tool_router_node → [按意图路由]
    ├── game    → game_info_node     → answer_node → self_check_node → END
    ├── rule    → platform_rules_node → answer_node → self_check_node → END
    ├── order   → order_node          → answer_node → self_check_node → END
    └── clarify → clarify_node                      → self_check_node → END
"""
import logging
from typing import TYPE_CHECKING

from langgraph.graph import StateGraph, END

from rent_agent.state import AgentState, create_initial_state
from rent_agent.nodes import (
    intent_node,
    tool_router_node,
    game_info_node,
    platform_rules_node,
    order_node,
    clarify_node,
    answer_node,
    self_check_node,
)

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

logger = logging.getLogger(__name__)


# ============================================================
#  1. 路由决策函数（读取 tool_router_node 写入的决策结果）
# ============================================================

def _read_route_decision(state: AgentState) -> str:
    """
    条件边函数：读取 tool_router_node 写入 state 的路由决策。

    返回值必须是 add_conditional_edges 映射表中的 key 之一。
    """
    decision = (
        state.get("context", {}).get("route_decision")
        or state.get("intent")
        or "clarify"
    )
    logger.info(f"🚦 条件边读取路由决策: {decision}")
    return decision


# ============================================================
#  2. 构建 Graph
# ============================================================

def build_graph() -> "CompiledStateGraph":
    """
    构建并编译 JoyRent Agent 的 LangGraph 工作流。

    Returns:
        编译后的 StateGraph，可直接调用 .invoke() 或 .stream()
    """
    graph = StateGraph(AgentState)

    # ---------- 注册所有节点 ----------
    graph.add_node("intent_node", intent_node)
    graph.add_node("tool_router_node", tool_router_node)
    graph.add_node("game_info_node", game_info_node)
    graph.add_node("platform_rules_node", platform_rules_node)
    graph.add_node("order_node", order_node)
    graph.add_node("clarify_node", clarify_node)
    graph.add_node("answer_node", answer_node)
    graph.add_node("self_check_node", self_check_node)

    # ---------- 设置入口 ----------
    graph.set_entry_point("intent_node")

    # ---------- 连接固定边 ----------
    # 意图识别 → 路由决策
    graph.add_edge("intent_node", "tool_router_node")

    # 业务节点（game/rule/order）→ 最终回答
    graph.add_edge("game_info_node", "answer_node")
    graph.add_edge("platform_rules_node", "answer_node")
    graph.add_edge("order_node", "answer_node")

    # clarify 节点自己生成回答，不需要 answer_node
    graph.add_edge("clarify_node", "self_check_node")

    # 最终回答 → 安全检查
    graph.add_edge("answer_node", "self_check_node")

    # 安全检查 → 结束
    graph.add_edge("self_check_node", END)

    # ---------- 条件边：路由分发 ----------
    graph.add_conditional_edges(
        "tool_router_node",
        _read_route_decision,
        {
            "game": "game_info_node",
            "rule": "platform_rules_node",
            "order": "order_node",
            "clarify": "clarify_node",
        },
    )

    # ---------- 编译 ----------
    compiled = graph.compile()
    logger.info("✅ JoyRent Agent Graph 编译完成")

    return compiled


# ============================================================
#  3. 便捷运行入口
# ============================================================

# 全局编译实例（懒加载）
_compiled_graph: "CompiledStateGraph | None" = None


def get_graph() -> "CompiledStateGraph":
    """获取全局唯一的编译后 Graph 实例（单例）"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def chat(user_input: str, user_id: str = None) -> str:
    """
    一句话调用入口（适合测试和 API 集成）

    Args:
        user_input: 用户输入的自然语言
        user_id: 用户 ID（可选，用于订单查询）

    Returns:
        Agent 的最终回答字符串

    Example:
        >>> from rent_agent.graph import chat
        >>> print(chat("塞尔达好玩吗？"))
        >>> print(chat("我的订单到哪了", user_id="42"))
    """
    graph = get_graph()
    initial_state = create_initial_state(user_input, user_id)

    logger.info(f"💬 收到用户输入: '{user_input}'")

    # invoke 会同步执行整个 Graph 流程
    final_state = graph.invoke(initial_state)

    answer = final_state.get("final_answer", "抱歉，系统遇到了一点小问题，请稍后再试~")

    # 打印调试摘要
    debug = final_state.get("debug_info", {})
    logger.info(
        f"📊 本轮执行摘要: "
        f"意图={final_state.get('intent')} | "
        f"置信度={final_state.get('intent_confidence', 0):.2f} | "
        f"路由={debug.get('route_decision')} | "
        f"状态={final_state.get('route_status')}"
    )

    return answer
