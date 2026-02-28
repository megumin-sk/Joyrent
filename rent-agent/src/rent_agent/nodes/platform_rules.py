"""
平台规则节点 (Platform Rules Node)

职责：
调用 PlatformRulesTool (封装了 Embedding 和 pgvector)，检索 JoyRent 的租赁业务规则。
"""
import logging
from typing import TYPE_CHECKING
from rent_agent.tools.platform_rules import PlatformRulesTool
from rent_agent.state import get_last_user_message

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)

def platform_rules_node(state: "AgentState") -> "AgentState":
    """LangGraph 节点：处理规则查询"""
    
    user_query = get_last_user_message(state)
    logger.info(f"📚 规则执行节点启动: 检索 '{user_query}' 相关规则")

    try:
        # 1. 执行向量搜索
        tool = PlatformRulesTool()
        results = tool.search(user_query)
        
        # 2. 提取内容
        rule_texts = [r["content"] for r in results]
        
        # 3. 更新状态
        state["retrieved_rules"] = rule_texts
        
        if rule_texts:
            state["route_status"] = "success"
            logger.info(f"✅ 成功检索到 {len(rule_texts)} 条规则")
        else:
            state["route_status"] = "failed"
            state["error_message"] = "未找到相关的平台规则说明"
            
    except Exception as e:
        logger.error(f"Rule Node 执行异常: {e}", exc_info=True)
        state["route_status"] = "failed"
        state["error_message"] = f"规则库连接失败: {str(e)}"
        
    return state
