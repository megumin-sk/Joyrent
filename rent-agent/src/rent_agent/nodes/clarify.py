"""
澄清引导节点 (Clarify Node)

职责：
当 Agent 无法确定用户意图，或者用户提供的信息不足以调用工具时，
调用大模型生成引导性的反问，帮助用户明确需求。
"""
import logging
from typing import TYPE_CHECKING
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from rent_agent.config import config
from rent_agent.state import get_last_user_message

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)


def clarify_node(state: "AgentState") -> "AgentState":
    """
    LangGraph 节点：生成澄清/引导问题

    触发场景：
    - 意图置信度低于阈值（tool_router 降级）
    - 意图分类为 clarify（用户说的话确实模糊）
    - 用户未登录但想查订单（需要引导登录）
    """
    user_input = get_last_user_message(state)
    clarify_count = state.get("clarify_count", 0)
    logger.info(f"🗣️ 触发澄清节点 [第 {clarify_count} 次]")

    # 使用大模型生成引导语（澄清需要自然语言能力，不是分类任务）
    llm = ChatOpenAI(
        model=config.ANSWER_MODEL,
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.DASHSCOPE_BASE_URL,
        temperature=0.7
    )

    # 构建动态 Prompt
    system_prompt = config.CLARIFY_SYSTEM_PROMPT

    # 从上游获取可能的错误信息（例如 tool_router 写入的"请先登录"）
    error_context = state.get("error_message", "")
    if error_context:
        system_prompt += f"\n\n【系统提示】当前遇到了以下状况，请在引导时温和地告知用户：{error_context}"

    # 如果已经澄清过多次了，在 prompt 里提醒模型换种问法
    if clarify_count >= 2:
        system_prompt += "\n\n【注意】你已经问过用户好几次了，这次请尝试给出一些具体的选项或推荐，而不是继续追问。"

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ]

    try:
        response = llm.invoke(messages)
        state["final_answer"] = response.content.strip()
        state["route_status"] = "success"

    except Exception as e:
        logger.error(f"Clarify Node 报错: {e}", exc_info=True)
        state["final_answer"] = "抱歉，小助手没听太明白，您能换个说法或者提供更多细节吗？😊"
        state["route_status"] = "failed"

    return state
