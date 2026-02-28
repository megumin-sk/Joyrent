"""
意图识别节点 (Intent Node)

职责：
接收用户输入，调用轻量 Flash 模型进行意图分类，
返回结构化 JSON：{"category": "xxx", "confidence": 0.xx}
"""
import logging
import json
import re
import time
from typing import TYPE_CHECKING
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from rent_agent.config import config
from rent_agent.state import get_last_user_message

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)

# 合法意图枚举（防止模型返回脏数据）
VALID_INTENTS = {"clarify", "rule", "game", "order"}


def intent_node(state: "AgentState") -> "AgentState":
    """
    LangGraph 节点：负责意图识别

    流程：
    1. 接收用户的最后一条消息
    2. 调用 Flash 模型 (tongyi-xiaomi-analysis-flash) 进行分类
    3. 解析 JSON 结果 {"category": ..., "confidence": ...}
    4. 校验意图合法性（不在枚举内则降级为 clarify）
    5. 更新 state["intent"] 和 state["intent_confidence"]
    """

    user_input = get_last_user_message(state)
    logger.info(f"🔍 正在识别意图: '{user_input}'")

    # 安全初始化 debug_info
    if not state.get("debug_info"):
        state["debug_info"] = {}

    # 1. 初始化 LLM
    llm = ChatOpenAI(
        model=config.INTENT_MODEL,
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.DASHSCOPE_BASE_URL,
        temperature=0.0  # 确保结果的确定性
    )

    # 2. 构建 Prompt
    messages = [
        SystemMessage(content=config.INTENT_SYSTEM_PROMPT),
        HumanMessage(content=user_input)
    ]

    try:
        # 3. 调用 LLM（带耗时监控）
        start_time = time.time()
        response = llm.invoke(messages)
        elapsed_ms = (time.time() - start_time) * 1000
        raw_content = response.content.strip()

        # 记录调试信息
        state["debug_info"]["intent_model_response"] = raw_content
        state["debug_info"]["intent_latency_ms"] = round(elapsed_ms, 1)

        # 4. 清理 Markdown 标记 (例如 ```json ... ```)
        cleaned_content = raw_content.replace("```json", "").replace("```", "").strip()

        # 5. 尝试提取 JSON (防御性正则，防止模型生成额外废话)
        match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
        if match:
            cleaned_content = match.group(0)

        result = json.loads(cleaned_content)

        intent = result.get("category", "clarify")
        confidence = float(result.get("confidence", 0.0))

        # 6. 校验意图合法性
        if intent not in VALID_INTENTS:
            logger.warning(f"⚠️ 模型返回了非法意图 '{intent}'，降级为 'clarify'")
            state["debug_info"]["intent_invalid_original"] = intent
            intent = "clarify"
            confidence = min(confidence, 0.3)  # 非法意图的置信度不能高

    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ JSON 解析失败: {e}，尝试纯文本回退")

        # 回退策略：模型可能只返回了一个单词（如 "game"）
        fallback = raw_content.lower().strip().strip('"').strip("'")
        if fallback in VALID_INTENTS:
            intent = fallback
            confidence = 0.7  # 纯文本回退给一个中等置信度
            logger.info(f"✅ 纯文本回退成功: '{intent}'")
        else:
            intent = "clarify"
            confidence = 0.0

    except Exception as e:
        logger.error(f"❌ 意图识别失败: {e}", exc_info=True)
        intent = "clarify"
        confidence = 0.0
        state["error_message"] = f"Intent Error: {str(e)}"

    # 7. 更新状态
    state["intent"] = intent
    state["intent_confidence"] = confidence

    logger.info(f"🎯 意图识别结果: {intent} (置信度: {confidence:.2f})")

    return state
