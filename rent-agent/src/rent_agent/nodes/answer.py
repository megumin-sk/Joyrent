import logging
from typing import TYPE_CHECKING
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from rent_agent.config import config
from rent_agent.state import get_last_user_message

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)

def answer_node(state: "AgentState") -> "AgentState":
    """
    LangGraph 节点：最终回答生成器 (Agent 的"嘴巴")
    
    它负责：
    1. 汇总在之前节点和工具执行过程中收集到的所有上下文 (Context)
    2. 加载大模型 (qwen3.5-plus)
    3. 基于给定的 System Prompt 和汇总的 Context，回答用户最初的问题
    """
    user_input = get_last_user_message(state)
    intent = state.get("intent")
    route_status = state.get("route_status", "pending")
    
    logger.info(f"🎤 开始生成最终回答 [意图: {intent}, 状态: {route_status}]")

    # 1. 初始化大模型 (使用推理能力更强、表达更地道的全尺寸模型)
    llm = ChatOpenAI(
        model=config.ANSWER_MODEL,
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.DASHSCOPE_BASE_URL,
        temperature=0.7 # 给予一定的创造性，让语气更自然生动
    )

    # 2. 从 state 中提取所有可能有用的上下文
    # 无论走的是什么节点，只要有数据，我们都尽量提供给大模型
    context_data = []
    
    # [游戏查询上下文]
    game_info = state.get("game_info")
    inventory_info = state.get("inventory_info")
    if game_info:
        # 将结构化的字典转为可读性强的文本给大模型
        context_data.append("【相关游戏资料】")
        context_data.append(f"游戏名称: {game_info.get('name', '未知')}")
        context_data.append(f"IGDB评分: {game_info.get('rating', '暂无评分')}")
        context_data.append(f"首发日期: {game_info.get('first_release_date', '未知')}")
        context_data.append(f"支持平台: {', '.join(game_info.get('platforms', []))}")
        context_data.append(f"游戏简介: {game_info.get('summary', '暂无中文简介')}")
        
        if inventory_info:
            context_data.append("【JoyRent 平台实时库存】")
            context_data.append(f"库存状态: 有货，剩余 {inventory_info.get('available_stock', 0)} 份" if inventory_info.get('available_stock', 0) > 0 else "库存状态: 暂时缺货")
            context_data.append(f"日租金: ¥{inventory_info.get('daily_rent_price', '未知')}/天")
        else:
            context_data.append("【JoyRent 平台实时库存】: 暂未上架或已无库存。")

    # [平台规则上下文]
    # 优先从顶层 state 读取（platform_rules_node 写入的位置）
    retrieved_rules = state.get("retrieved_rules") or state.get("context", {}).get("retrieved_rules")
    if retrieved_rules:
        context_data.append("【JoyRent 平台相关规则参考】")
        for i, rule in enumerate(retrieved_rules):
            context_data.append(f"规则 {i+1}: {rule}")

    # [订单查询上下文]
    # 优先从顶层 state 读取（order_node 写入的位置）
    order_info = state.get("order_info") or state.get("context", {}).get("order_info")
    if order_info:
        context_data.append("【用户订单查询结果】")
        if isinstance(order_info, list) and len(order_info) > 0:
            for o in order_info:
                # 只挑几个关键字段给 LLM 看
                context_data.append(f"订单号(ID): {o.get('id')}")
                context_data.append(f"包含游戏: {o.get('game_title')}")
                # 状态转换 (这部分如果是枚举值，大模型通常能理解10/20等的含义，但如果是中文更好)
                status_map = {10:"待支付", 20:"待发货", 30:"租赁中", 40:"归还中", 50:"已完成", 60:"已取消"}
                status_text = status_map.get(o.get('status'), str(o.get('status')))
                context_data.append(f"订单状态: {status_text}")
                if o.get("days_left") is not None:
                     context_data.append(f"距离计划归还(天): 剩 {o.get('days_left')} 天")
                if o.get("tracking_number_send"):
                     context_data.append(f"发货单号: {o.get('tracking_number_send')}")
        else:
             context_data.append("近期无相关订单信息。")
             
    # [错误信息处理]
    if route_status == "failed" and state.get("error_message"):
        context_data.append(f"【系统后台警告信】查询过程遇到障碍说明，请用温和的话术转述给用户：{state.get('error_message')}")

    context_str = "\n".join(context_data) if context_data else "暂无后台具体资料提供，请根据常识和客服角色直接安抚回答。"

    # 3. 构建 Prompt
    system_prompt = f"""{config.ANSWER_SYSTEM_PROMPT}

请基于以下【系统后台资料】回答用户的提问。不要生硬地复制后台资料，而是要以“JoyRent客服小助手”的口吻，用温暖、有服务意识、生动活泼的语言告诉用户结果。如果遇到缺货、未查到订单等负面情况，请多多安抚。

====== 核心资料参考 ======
{context_str}
==========================
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ]

    try:
        # 4. 生成回答
        response = llm.invoke(messages)
        final_answer = response.content.strip()
        state["final_answer"] = final_answer
        
        # 调试信息
        if not state.get("debug_info"):
            state["debug_info"] = {}
        state["debug_info"]["answer_context_length"] = len(context_str)
        logger.info(f"✅ 回答生成成功，长度: {len(final_answer)}字")
        
    except Exception as e:
        logger.error(f"回答生成节点报错: {e}", exc_info=True)
        # 极端情况兜底
        state["final_answer"] = "哎呀，小助手的大脑突然有点短路 😵 麻烦您稍后再试一下呢~"
        
    return state
