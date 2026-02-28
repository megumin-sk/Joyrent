"""
工具路由节点 (Tool Router Node)

职责：
根据 intent_node 的意图识别结果，决定下一步应该走哪条执行分支。
它本身不执行任何业务逻辑，只做"分拣"。

在 LangGraph 中，本节点返回的字符串将作为条件边 (conditional edge)
的路由键，由 graph.py 中的 add_conditional_edges 映射到具体的下游节点。

路由规则：
┌──────────────┬──────────────────────┬────────────────────────────────┐
│ 意图 (intent)│ 路由键 (route key)   │ 目标节点                       │
├──────────────┼──────────────────────┼────────────────────────────────┤
│ game         │ "game"               │ game_info_node                 │
│ rule         │ "rule"               │ platform_rules_node            │
│ order        │ "order"              │ order_node                     │
│ clarify      │ "clarify"            │ clarify_node (或直接 answer)   │
│ (异常兜底)   │ "clarify"            │ 安全默认路径                   │
└──────────────┴──────────────────────┴────────────────────────────────┘
"""
import logging
from typing import TYPE_CHECKING, Literal

from rent_agent.config import config

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)

# 路由键类型定义（与 graph.py 中的 conditional_edges 映射表严格对应）
RouteKey = Literal["game", "rule", "order", "clarify"]

# 低置信度阈值：低于该值时，无论识别出什么意图，都强制降级为 clarify
LOW_CONFIDENCE_THRESHOLD = 0.6


def route_by_intent(state: "AgentState") -> RouteKey:
    """
    LangGraph 条件路由函数（纯函数，不修改 state）

    用法（在 graph.py 中）：
        graph.add_conditional_edges(
            "intent_node",
            route_by_intent,
            {
                "game":    "game_info_node",
                "rule":    "platform_rules_node",
                "order":   "order_node",
                "clarify": "clarify_node",
            }
        )

    Returns:
        路由键字符串，决定下一个执行的节点名
    """
    intent = state.get("intent")
    confidence = state.get("intent_confidence", 0.0)

    logger.info(f"🚦 路由决策中 [意图: {intent}, 置信度: {confidence:.2f}]")

    # ========== 规则 1: 置信度过低 → 强制澄清 ==========
    # 意图识别模型不够确定时，宁可多问一句，也别走错分支
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        logger.warning(
            f"⚠️ 置信度过低 ({confidence:.2f} < {LOW_CONFIDENCE_THRESHOLD})，"
            f"原始意图 '{intent}' 被降级为 'clarify'"
        )
        return "clarify"

    # ========== 规则 2: 澄清次数耗尽 → 兜底到游戏查询 ==========
    # 如果已经反复澄清了多次用户还是说不清楚，
    # 就默认按"游戏查询"处理（因为这是 JoyRent 最核心的场景）
    clarify_count = state.get("clarify_count", 0)
    if intent == "clarify" and clarify_count >= config.MAX_CLARIFY_RETRIES:
        logger.warning(
            f"⚠️ 澄清次数已达上限 ({clarify_count}/{config.MAX_CLARIFY_RETRIES})，"
            f"降级为默认路由 'game'"
        )
        return "game"

    # ========== 规则 3: 订单查询 → 前置登录校验 ==========
    # 如果用户未登录就想查订单，直接引导走 clarify 提示登录
    if intent == "order" and not state.get("is_authenticated", False):
        logger.info("🔒 用户未登录，订单路由降级为 'clarify'（将提示登录）")
        # 在 state 中写入错误信息，让 clarify/answer 节点据此生成登录引导话术
        state["error_message"] = "查询订单需要先登录哦，请先登录您的 JoyRent 账号~"
        return "clarify"

    # ========== 规则 4: 正常路由 ==========
    valid_routes: set[RouteKey] = {"game", "rule", "order", "clarify"}
    if intent in valid_routes:
        logger.info(f"✅ 路由确认: {intent}")
        return intent

    # ========== 兜底: 未知意图 → 安全降级 ==========
    logger.error(f"❌ 未知意图类型: '{intent}'，安全降级为 'clarify'")
    return "clarify"


def tool_router_node(state: "AgentState") -> "AgentState":
    """
    LangGraph 节点版本：路由决策 + 状态标记

    与纯函数 route_by_intent 不同，这个版本会：
    1. 执行路由决策
    2. 把决策结果写入 state["context"]["route_decision"]，方便调试追踪
    3. 如果是 clarify，还会自增 clarify_count

    适用于需要在路由节点中做一些"副作用"操作的场景。
    如果你的 graph.py 直接用 add_conditional_edges + route_by_intent 纯函数，
    则本函数可以不用。
    """
    intent = state.get("intent")
    confidence = state.get("intent_confidence", 0.0)

    logger.info(f"🚦 Tool Router 节点启动 [意图: {intent}, 置信度: {confidence:.2f}]")

    # 执行路由决策
    route_decision = route_by_intent(state)

    # ========== 副作用 1: 记录路由决策到 debug_info ==========
    if "debug_info" not in state or state["debug_info"] is None:
        state["debug_info"] = {}
    state["debug_info"]["route_decision"] = route_decision
    state["debug_info"]["route_original_intent"] = intent
    state["debug_info"]["route_confidence"] = confidence

    # ========== 副作用 2: clarify 计数器自增 ==========
    if route_decision == "clarify":
        state["clarify_count"] = state.get("clarify_count", 0) + 1
        logger.info(f"🔄 澄清计数: {state['clarify_count']}/{config.MAX_CLARIFY_RETRIES}")

    # 把路由决策也写入 context，供下游节点感知
    if "context" not in state or state["context"] is None:
        state["context"] = {}
    state["context"]["route_decision"] = route_decision

    logger.info(f"🚦 路由决策完成: '{intent}' → '{route_decision}'")

    return state
