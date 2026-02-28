"""
订单节点 (Order Node)

职责：
调用 OrderTool (对接 MySQL 业务库)，查询用户的历史订单、物流状态或处理归还申请。
"""
import logging
from typing import TYPE_CHECKING
from rent_agent.tools.order_service import OrderTool
from rent_agent.state import get_last_user_message

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)

def order_node(state: "AgentState") -> "AgentState":
    """LangGraph 节点：处理订单查询请求"""
    
    user_id = state.get("user_id")
    user_query = get_last_user_message(state)
    logger.info(f"📦 订单执行节点启动 [User: {user_id}]")

    # 1. 登录前置检查 (虽然路由节点拦截了一次，这里做双重保险)
    if not user_id:
        state["route_status"] = "failed"
        state["error_message"] = "由于未检测到登录状态，无法查询您的订单信息。请先登录账号哦~"
        return state

    try:
        tool = OrderTool()
        
        # 2. 简单的子意图判断
        query_type = "recent"
        if any(w in user_query for w in ["在租", "没还", "库存", "日期"]):
            query_type = "renting"
            
        # 3. 执行查询
        orders = tool.query_my_orders(int(user_id), intent_detail=query_type)
        
        # 4. 更新状态
        state["order_info"] = orders
        
        if orders:
            state["route_status"] = "success"
        else:
            state["route_status"] = "degraded"
            state["error_message"] = "您近期似乎还没有在 JoyRent 租赁过游戏呢"
            
    except Exception as e:
        logger.error(f"Order Node 执行异常: {e}", exc_info=True)
        state["route_status"] = "failed"
        state["error_message"] = f"订单系统查询遇到点小麻烦: {str(e)}"
        
    return state
