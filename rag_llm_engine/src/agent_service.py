from langchain.agents import create_agent
from config import Config
from tools import search_game_info, search_platform_rules
from model_factory import ModelFactory
from database import get_db_connection
from langchain_community.chat_message_histories import ChatMessageHistory
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dashscope import MultiModalEmbedding
from utils import smart_split
from typing import Optional, List

app = FastAPI(title="JoyRent Agent API")

# 配置 CORS 允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8010",
        "http://127.0.0.1:8010",
        "http://localhost:5173",  # 常用 Vite 默认端口
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 LLM 实例
llm = ModelFactory.get_llm()

# 组装工具列表
tools = [search_game_info, search_platform_rules]

agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=Config.AGENT_SYSTEM_PROMPT,
    debug=True  # 开启后，你能在控制台看到完整的思考过程
)

# 全局内存记忆存储 (替代 Redis)
sessions_storage = {}

def get_chat_history(session_id: str) -> ChatMessageHistory:
    if session_id not in sessions_storage:
        sessions_storage[session_id] = ChatMessageHistory()
    return sessions_storage[session_id]

from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    game_id: int = None
    session_id: str = "default_session"

class AddDocRequest(BaseModel):
    game_id: Optional[int] = None
    category: str
    content: str

class SearchRequest(BaseModel):
    query: str
    game_id: Optional[int] = None

# FastAPI 路由 (适配前端 /rag/ask)
@app.post("/rag/ask")
async def chat_with_agent(request: ChatRequest):
    """
    接收用户输入，分析意图并调用 Agent。
    """
    user_input = request.query
    session_id = request.session_id
    
    # 1. 从内存获取历史记录
    history = get_chat_history(session_id)
    
    # 2. 获取历史记录（由 LangChain 自动从 Redis 捞取消息对象）
    full_history = history.messages
    
    # 3. 滑动窗口：仅提取最近的 N 条消息（防止上下文爆炸）
    # 例如 Config.MEMORY_WINDOW_SIZE 为 10，则只留最近 10 条
    limited_history = full_history[-Config.MEMORY_WINDOW_SIZE:] if Config.MEMORY_WINDOW_SIZE > 0 else full_history
    
    # 4. 组装对话上下文：截断后的历史 + 当前问题
    current_messages = limited_history + [("human", user_input)]
    
    # 5. 调用 Agent (ReAct 模式)
    result = agent_executor.invoke({"messages": current_messages})
    
    # 6. 获取回答内容
    response_content = result["messages"][-1].content
    
    # 7. 同步更新 Redis 历史记录 (这里依然存储全量，但调用模型时会截断)
    history.add_user_message(user_input)
    history.add_ai_message(response_content)
    
    # 返回结构
    return {
        "code": 200,
        "msg": "success",
        "answer": response_content,
        "output": response_content
    }

# --- RAG 基础接口 (供前端管理后台使用) ---

@app.post("/rag/add")
async def add_document(request: AddDocRequest):
    """手动添加知识到向量库"""
    if not request.content:
        raise HTTPException(status_code=400, detail="内容不能为空")

    try:
        # 1. 智能切片 (复用 utils.py 的逻辑)
        chunks = smart_split(request.content)
        
        # 2. 生成向量 (适配 1024 维的 MultiModalEmbedding)
        embeddings = []
        resp = MultiModalEmbedding.call(
            model=Config.EMBEDDING_MODEL,
            input=[{'text': chunk} for chunk in chunks]
        )
        
        if resp.status_code == 200:
            embeddings = [item['embedding'] for item in resp.output['embeddings']]
        else:
            raise Exception(f"向量化失败: {resp.message}")

        # 3. 写入 PostgreSQL (pgvector)
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                data_values = [
                    (request.game_id, request.category, chunk, vec)
                    for chunk, vec in zip(chunks, embeddings)
                ]
                cur.executemany(
                    "INSERT INTO documents (game_id, category, content, embedding) VALUES (%s, %s, %s, %s)",
                    data_values
                )
            conn.commit()
        finally:
            conn.close()

        return {"code": 200, "msg": f"成功入库 {len(chunks)} 条片段"}
    except Exception as e:
        print(f"Error adding doc: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rag/search")
async def search_document(query: str, game_id: int = None):
    """检索测试接口 (供前端调试使用)"""
    if not query:
        raise HTTPException(status_code=400, detail="搜索词不能为空")
    
    try:
        # 1. 查询向量化
        resp = MultiModalEmbedding.call(
            model=Config.EMBEDDING_MODEL,
            input=[{'text': query}]
        )
        if resp.status_code != 200:
            raise Exception(f"向量化失败: {resp.message}")
        
        query_vec = resp.output['embeddings'][0]['embedding']

        # 2. 数据库检索
        conn = get_db_connection()
        cur = conn.cursor()
        
        sql = "SELECT game_id, category, content, 1 - (embedding <=> %s::vector) as similarity FROM documents WHERE 1=1"
        params = [query_vec]
        
        if game_id:
            sql += " AND (game_id = %s OR game_id IS NULL)"
            params.append(game_id)
            
        sql += f" ORDER BY embedding <=> %s::vector LIMIT {Config.TOP_K}"
        params.append(query_vec)
        
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "code": 200,
            "results": [
                {"game_id": r[0], "category": r[1], "content": r[2], "similarity": float(r[3])}
                for r in rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    # 启动服务，监听 5001 端口（匹配 frontend rag.js）
    uvicorn.run(app, host="0.0.0.0", port=5001)


