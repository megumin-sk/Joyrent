"""
JoyRent Agent — FastAPI 应用

提供 RESTful API 供前端或其他服务调用 Agent。

启动方式：
    uvicorn rent_agent.api.app:app --reload --port 8001
"""
import logging
import time
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from rent_agent.config import config
from rent_agent.logging_setup import configure_logging
from rent_agent.graph import get_graph, chat
from rent_agent.state import create_initial_state
from rent_agent.api.schemas import (
    ChatRequest,
    ChatResponse,
    DebugResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)

# 无论通过 `python -m rent_agent.main` 还是 `uvicorn rent_agent.api.app:app`
# 启动，都确保 rent_agent.* 的运行日志可见。
configure_logging()

# 是否启用调试模式（通过环境变量控制）
DEBUG_MODE = os.getenv("AGENT_DEBUG", "false").lower() == "true"


# ============================================================
#  应用生命周期
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用启动/关闭时的hook"""
    # 启动时：预编译 Graph（避免首次请求慢）
    logger.info("⏳ 正在预编译 Agent Graph...")
    get_graph()
    logger.info("✅ Graph 编译完成，服务就绪")
    logger.info(f"📋 意图模型: {config.INTENT_MODEL}")
    logger.info(f"📋 回答模型: {config.ANSWER_MODEL}")
    logger.info(f"📋 嵌入模型: {config.EMBEDDING_MODEL}")
    yield
    # 关闭时
    logger.info("👋 JoyRent Agent 已关闭")



# ============================================================
#  创建 FastAPI 实例
# ============================================================

app = FastAPI(
    title="JoyRent Agent API",
    description="JoyRent 游戏租赁平台 AI 客服助手 API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件（允许前端跨域调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应改为具体前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
#  路由定义
# ============================================================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    健康检查接口

    用于负载均衡器或 k8s 探针检测服务是否存活。
    """
    return HealthResponse(
        models={
            "intent": config.INTENT_MODEL,
            "answer": config.ANSWER_MODEL,
            "embedding": config.EMBEDDING_MODEL,
        }
    )


@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat_endpoint(request: ChatRequest):
    """
    核心对话接口

    接收用户消息，经过意图识别 → 工具路由 → 数据检索 → 推理回答的完整流程，
    返回 Agent 的最终回答。

    - **message**: 用户输入（必填）
    - **user_id**: 用户 ID（查订单时需要）
    - **session_id**: 会话 ID（预留多轮对话）
    """
    start_time = time.time()
    logger.info(f"➡️ /chat 请求进入: session_id={request.session_id} user_id={request.user_id}")

    try:
        # 1. 构建初始状态
        graph = get_graph()
        initial_state = create_initial_state(
            user_input=request.message,
            user_id=request.user_id,
        )

        # 2. 执行 Graph
        final_state = graph.invoke(initial_state)

        # 3. 提取结果
        answer = final_state.get("final_answer", "抱歉，系统遇到了一点小问题，请稍后再试~")
        elapsed_ms = (time.time() - start_time) * 1000

        logger.info(
            f"💬 对话完成 [{elapsed_ms:.0f}ms] "
            f"意图={final_state.get('intent')} "
            f"状态={final_state.get('route_status')}"
        )

        return ChatResponse(
            answer=answer,
            intent=final_state.get("intent"),
            confidence=final_state.get("intent_confidence"),
            route_status=final_state.get("route_status"),
        )

    except Exception as e:
        logger.error(f"❌ /chat 接口异常: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Agent 内部错误: {str(e)}",
        )


@app.post("/chat/debug", response_model=DebugResponse, tags=["Agent"])
async def chat_debug_endpoint(request: ChatRequest):
    """
    调试版对话接口（开发环境使用）

    除了正常回答外，还会返回完整的调试信息：
    - 意图识别的原始模型响应
    - 路由决策过程
    - 意图识别耗时
    - 上下文长度等
    """
    start_time = time.time()
    logger.info(f"➡️ /chat/debug 请求进入: session_id={request.session_id} user_id={request.user_id}")

    try:
        graph = get_graph()
        initial_state = create_initial_state(
            user_input=request.message,
            user_id=request.user_id,
        )

        final_state = graph.invoke(initial_state)

        answer = final_state.get("final_answer", "抱歉，系统遇到了一点小问题，请稍后再试~")
        debug_info = final_state.get("debug_info", {})
        elapsed_ms = (time.time() - start_time) * 1000

        # 追加总耗时到 debug_info
        debug_info["total_elapsed_ms"] = round(elapsed_ms, 1)

        return DebugResponse(
            answer=answer,
            intent=final_state.get("intent"),
            confidence=final_state.get("intent_confidence"),
            route_status=final_state.get("route_status"),
            debug_info=debug_info,
            route_decision=debug_info.get("route_decision"),
            intent_latency_ms=debug_info.get("intent_latency_ms"),
        )

    except Exception as e:
        logger.error(f"❌ /chat/debug 接口异常: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Agent 内部错误: {str(e)}",
        )
