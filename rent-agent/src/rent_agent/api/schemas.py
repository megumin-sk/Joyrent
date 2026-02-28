"""
API 请求/响应模型定义

使用 Pydantic v2 进行数据校验和序列化。
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==================== 请求模型 ====================

class ChatRequest(BaseModel):
    """聊天请求体"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="用户输入的消息",
        examples=["塞尔达好玩吗？", "运费怎么算？", "我的订单到哪了？"],
    )
    user_id: Optional[str] = Field(
        default=None,
        description="用户 ID（查询订单时必传）",
        examples=["42"],
    )
    session_id: Optional[str] = Field(
        default=None,
        description="会话 ID（用于多轮对话追踪，预留字段）",
    )


# ==================== 响应模型 ====================

class ChatResponse(BaseModel):
    """聊天响应体"""
    answer: str = Field(..., description="Agent 的最终回答")
    intent: Optional[str] = Field(default=None, description="识别出的意图类型")
    confidence: Optional[float] = Field(default=None, description="意图置信度")
    route_status: Optional[str] = Field(default=None, description="路由执行状态")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="响应时间戳",
    )


class DebugResponse(ChatResponse):
    """带调试信息的响应（仅开发环境返回）"""
    debug_info: Optional[dict] = Field(default=None, description="调试详情")
    route_decision: Optional[str] = Field(default=None, description="路由决策")
    intent_latency_ms: Optional[float] = Field(default=None, description="意图识别耗时(ms)")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    service: str = "rent-agent"
    version: str = "2.0.0"
    models: dict = Field(
        default_factory=dict,
        description="当前使用的模型配置",
    )
