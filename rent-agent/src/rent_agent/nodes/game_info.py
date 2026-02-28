"""
游戏信息节点 (Game Info Node)

职责：
调用 GameInfoTool (封装了 IGDB API 和 MySQL) 获取游戏详情及 JoyRent 实时库存。
"""
import logging
from typing import TYPE_CHECKING
from rent_agent.tools.game_info import GameInfoTool
from rent_agent.state import get_last_user_message

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)

def game_info_node(state: "AgentState") -> "AgentState":
    """LangGraph 节点：处理游戏查询请求"""
    
    # 1. 提取输入（优先从 context 获取提取出的游戏名，否则用原始消息）
    game_name = state.get("context", {}).get("game_name") or get_last_user_message(state)
    logger.info(f"🎮 游戏执行节点启动: 查询 '{game_name}'")

    if not game_name:
        state["route_status"] = "failed"
        state["error_message"] = "未提供有效游戏名称"
        return state

    try:
        # 2. 调用原子工具
        tool = GameInfoTool()
        result = tool.search(game_name)
        
        # 3. 将工具返回的数据回填至全局 State
        state["game_info"] = result.get("game_info")
        state["inventory_info"] = result.get("inventory")
        
        # 记录来源用于调试
        if "debug_info" not in state: state["debug_info"] = {}
        state["debug_info"]["game_search_source"] = result.get("source")
        
        if result.get("status") == "success":
            # 如果查到了游戏但没库存，属于"降级"成功
            state["route_status"] = "success" if result.get("inventory") else "degraded"
            if not result.get("inventory"):
                state["error_message"] = "哎呀，这款游戏目前暂未上架或已租完"
        else:
            state["route_status"] = "failed"
            state["error_message"] = f"抱歉，在 JoyRent 库中没找到 '{game_name}' 的相关记录"
            
    except Exception as e:
        logger.error(f"Game Node 执行异常: {e}", exc_info=True)
        state["route_status"] = "failed"
        state["error_message"] = f"游戏库查询暂时不可用: {str(e)}"
        
    return state
