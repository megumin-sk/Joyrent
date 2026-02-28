"""
JoyRent Agent 应用入口

启动方式：
    # 开发环境（热重载）
    python -m rent_agent.main

    # 或直接用 uvicorn
    uvicorn rent_agent.api.app:app --reload --port 8001
"""
import sys
import logging
import uvicorn
from rent_agent.logging_setup import configure_logging

configure_logging()


def main():
    """启动 FastAPI 服务"""
    # 用 print 确保启动信息一定能看到（不受 logging 配置影响）
    print("=" * 56, file=sys.stderr, flush=True)
    print("🚀 JoyRent Agent v2.0 正在启动...", file=sys.stderr, flush=True)
    print(f"📡 监听地址: http://0.0.0.0:8001", file=sys.stderr, flush=True)
    print(f"📖 Swagger:  http://localhost:8001/docs", file=sys.stderr, flush=True)
    print("=" * 56, file=sys.stderr, flush=True)

    uvicorn.run(
        "rent_agent.api.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        log_config=None,
    )


if __name__ == "__main__":
    main()
