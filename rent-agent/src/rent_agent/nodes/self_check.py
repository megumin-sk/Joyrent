"""
安全检查节点 (Self-Check Node)

职责：
在对话结束前，对生成的回答进行快速扫描，防止出现逻辑冲突或不文明用语。
"""
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)

def self_check_node(state: "AgentState") -> "AgentState":
    """
    LangGraph 节点：内容自检
    """
    answer = state.get("final_answer", "")
    
    if not answer:
        return state

    # 目前实现较为简单，主要作为架构占位
    # 后续可以接入敏感词过滤或 LLM 质量评分
    forbidden_words = ["垃圾", "非法", "诈骗"]
    
    for word in forbidden_words:
        if word in answer:
            logger.warning(f"⚠️ 触发安全拦截: 发现敏感词 '{word}'")
            state["final_answer"] = "抱歉，由于系统触发安全策略，该条回复无法显示。请尝试换个问法。"
            break
            
    return state
