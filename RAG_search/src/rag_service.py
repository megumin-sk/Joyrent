import uvicorn
import dashscope
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dashscope import TextEmbedding
from typing import List, Dict, Any, Optional
import sys
import os
import tempfile
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.database import get_db_connection, init_db, get_games_stock
from src.utils import smart_split, smart_split_with_metrics, load_and_split
from src.model_factory import ModelFactory
import torch
import torch.nn.functional as F

# 设置 API Key
dashscope.api_key = Config.DASHSCOPE_API_KEY

app = FastAPI(title="RAG Search Service")

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AddDocRequest(BaseModel):
    game_id: Optional[int]
    category: str
    content: str

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    chunks_count: int
    metadata: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str
    game_id: int = None # 可选：只搜某个游戏

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化数据库和模型"""
    init_db()
    
    global bert_model, bert_tokenizer, device
    print(f"Loading BERT Intent Model from {Config.BERT_MODEL_PATH}...")
    try:
        device = torch.device(Config.DEVICE)
        bert_tokenizer = ModelFactory.get_tokenizer(Config.BERT_MODEL_PATH)
        bert_model = ModelFactory.get_model(
             model_path=Config.BERT_MODEL_PATH
        )
        bert_model.to(device)
        bert_model.eval() # 切换到评估模式
        print("✅ BERT Model loaded successfully.")
    except Exception as e:
        import traceback
        print(f"❌ Failed to load BERT model: {e}")
        print(traceback.format_exc())

@app.post("/rag/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    game_id: Optional[int] = None,
    category: str = "document"
):
    """
    上传文档（支持 PDF, WORD, EXCEL, MARKDOWN, HTML, TXT）
    自动加载并切分，然后存入向量库
    
    Args:
        file: 上传的文件（PDF, DOCX, TXT 等）
        game_id: 关联的游戏 ID（可选）
        category: 文档类别
    
    Returns:
        上传结果，包含切分数量和元数据
    """
    if not file:
        raise HTTPException(status_code=400, detail="File is required")
    
    # 验证文件类型
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.html', '.htm'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    temp_file_path = None
    try:
        # Step 1: 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_file_path = tmp.name
            content = await file.read()
            tmp.write(content)
        
        print(f"📄 Processing file: {file.filename} ({len(content)} bytes)")
        
        # Step 2: 加载和切分文档
        chunks, metadata = load_and_split(temp_file_path, max_length=500, overlap=50)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="File content is empty or cannot be processed")
        
        print(f"✅ Split into {len(chunks)} chunks")
        
        # Step 3: 生成向量并存入数据库
        embeddings = []
        resp = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v1,
            input=chunks
        )
        
        if resp.status_code == 200:
            raw_embeddings = resp.output['embeddings']
            embeddings = [item['embedding'] for item in raw_embeddings]
        else:
            raise Exception(f"DashScope Embedding Error: {resp.message}")
        
        # Step 4: 批量存入 PostgreSQL
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                data_values = [
                    (game_id, category, chunk, vec)
                    for chunk, vec in zip(chunks, embeddings)
                ]
                
                insert_sql = """
                INSERT INTO rag_documents (game_id, category, content, embedding)
                VALUES (%s, %s, %s, %s)
                """
                
                cur.executemany(insert_sql, data_values)
                conn.commit()
                print(f"✅ Inserted {len(data_values)} vectors into database")
        finally:
            conn.close()
        
        return FileUploadResponse(
            success=True,
            message=f"Successfully processed {file.filename}",
            chunks_count=len(chunks),
            metadata=metadata
        )
        
    except Exception as e:
        import traceback
        print(f"❌ Error processing file: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Step 5: 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass

@app.post("/rag/add")
async def add_document(request: AddDocRequest):
    """添加文档到向量库"""
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")

    try:
        # 1. 智能切片
        chunks = smart_split(request.content)
        print(f"Content split into {len(chunks)} chunks.")
        
        # 2. 批量生成向量
        embeddings = []
        
        resp = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v1,
            input=chunks
        )
        
        if resp.status_code == 200:
            raw_embeddings = resp.output['embeddings']
            embeddings = [item['embedding'] for item in raw_embeddings]
        else:
            raise Exception(f"DashScope Embedding Error: {resp.message}")

        # 3. 批量存入 PostgreSQL
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
            
            conn.commit() # 全部成功才提交
            print(f"Successfully inserted {len(data_values)} records.")
            
        except Exception as db_err:
            conn.rollback() # 有错就全部回滚
            raise db_err
        finally:
            conn.close()

        return {"message": f"Successfully added {len(chunks)} document chunks."}
            
    except Exception as e:
        print(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from dashscope import Generation

# 全局模型变量
bert_model = None
bert_tokenizer = None
device = None

def predict_intent(query: str) -> str:
    """
    使用 BERT 模型识别用户意图
    返回: 'rule', 'game', 或 'all'
    """
    global bert_model, bert_tokenizer, device
    
    if not bert_model or not bert_tokenizer:
        print("Warning: BERT model not loaded, falling back to 'all'")
        return 'all'
        
    try:
        # 1. 预处理
        inputs = bert_tokenizer(
            query, 
            return_tensors="pt", 
            truncation=True, 
            max_length=128, 
            padding=True
        ).to(device)
        
        # 2. 推理
        with torch.no_grad():
            outputs = bert_model(**inputs)
            logits = outputs.logits
        
        # 3. 获取结果
        probs = F.softmax(logits, dim=1)
        # 获取最大概率的索引
        pred_idx = torch.argmax(probs, dim=1).item()
        # 获取最大概率值
        confidence = probs[0][pred_idx].item()
        
        # 映射回标签字符串
        intent = Config.BERT_LABEL_MAP.get(pred_idx, 'all')
        
        print("\n---------------------------------------------------")
        print(f"🕵️ BERT Intent Recognition Details for: '{query}'")
        for idx, score in enumerate(probs[0]):
            label_name = Config.BERT_LABEL_MAP.get(idx, f"unknown_{idx}")
            bar_len = int(score.item() * 20)
            bar = '█' * bar_len + '░' * (20 - bar_len)
            print(f"   - {label_name.ljust(6)}: {bar} {score.item():.4f}")
        print(f"👉 Final Decision: {intent} (Confidence: {confidence:.4f})")
        print("---------------------------------------------------\n")
        
        # 可选：如果置信度太低，可以强制转为 'all'
        if confidence < 0.6:
            print(f"Confidence too low ({confidence:.4f}), fallback to 'all'")
            return 'all'
            
        return intent

    except Exception as e:
        print(f"Intent recognition error: {e}")
        return 'all'

# --- 核心检索逻辑抽取 ---
def _retrieve_documents(query: str, game_id: int = None):
    # 1. 意图识别
    intent = predict_intent(query)
    print(f"User Query: {query} | Predicted Intent: {intent}")

    # 2. 向量化
    resp = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v1,
        input=query
    )
    
    if resp.status_code != 200:
        raise Exception(f"Embedding failed: {resp.message}")
        
    query_embedding = resp.output['embeddings'][0]['embedding']
    # 3. 数据库检索
    conn = get_db_connection()
    cur = conn.cursor()
    
    sql = f"""
        SELECT game_id, category, content, 1 - (embedding <=> %s::vector) as similarity
        FROM documents
        WHERE 1=1
    """
    params = [query_embedding]
    
    if intent != 'all':
        sql += " AND category = %s"
        params.append(intent)

    if game_id:
        sql += " AND (game_id = %s OR game_id IS NULL)"
        params.append(game_id)
        
    sql += f" ORDER BY embedding <=> %s::vector LIMIT {Config.TOP_K}"
    params.append(query_embedding)
    
    print(f"====== [PGSQL DEBUG] Executing: {sql.replace(chr(10), ' ').strip()} ======")
    cur.execute(sql, tuple(params))
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return intent, results

@app.get("/rag/search")
async def search_document(query: str, game_id: int = None):
    """返回检索到的文档片段"""
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    try:
        intent, results = _retrieve_documents(query, game_id)
        return {
            "intent": intent,
            "results": [
                {
                    "game_id": row[0],
                    "category": row[1],
                    "content": row[2], 
                    "similarity": float(row[3])
                } for row in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AskRequest(BaseModel):
    query: str
    game_id: Optional[int] = None

@app.post("/rag/ask")
async def ask_question(request: AskRequest):
    """RAG 问答：检索 + 生成回答"""
    if not request.query:
        raise HTTPException(status_code=400, detail="Query is required")
        
    try:
        # Step 1: 检索
        intent, results = _retrieve_documents(request.query, request.game_id)
        
        if not results:
            return {"answer": "抱歉，我的知识库里暂时没有找到相关信息，您可以换个说法试试。", "sources": []}
            
        # Step 2: 整理上下文
        # 提取 content 字段，拼接起来
        context_list = [f"【资料{i+1}】: {row[2]}" for i, row in enumerate(results)]
        
        # --- 新增: 获取相关游戏的库存信息 ---
        # 收集涉及的 game_id (排除 None)
        related_game_ids = set()
        if request.game_id:
            related_game_ids.add(request.game_id)
        
        for row in results:
            if row[0]: # row[0] is game_id
                related_game_ids.add(row[0])
                
        if related_game_ids:
            try:
                stock_map = get_games_stock(list(related_game_ids))
                stock_info_strs = []
                for gid, info in stock_map.items():
                    stock_info_strs.append(f"游戏《{info['title']}》当前剩余库存：{info['available_stock']}份")
                
                if stock_info_strs:
                    context_list.append("\n【实时库存信息】:\n" + "\n".join(stock_info_strs))
            except Exception as e:
                print(f"Failed to fetch stock info: {e}")
        # ----------------------------------

        context_str = "\n\n".join(context_list)
        
        # Step 3: 调用模型生成回答 (Generation)
        prompt = Config.RAG_ANSWER_PROMPT.format(context=context_str, query=request.query)
        
        print(f"\n====== [RAG FINAL PROMPT] ======\n{prompt}\n==============================\n")
        
        # Retry logic for LLM call
        import time
        max_retries = 3
        gen_resp = None
        
        for attempt in range(max_retries):
            try:
                gen_resp = Generation.call(
                    model=Generation.Models.qwen_turbo,
                    prompt=prompt
                )
                if gen_resp.status_code == 200:
                    break
                else:
                    print(f"⚠️ LLM Call failed (Status {gen_resp.status_code}, Attempt {attempt+1}/{max_retries}): {gen_resp.message}")
            except Exception as e:
                print(f"⚠️ LLM Network/SSL Error (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=500, detail=f"LLM Service Unavailable: {str(e)}")
                time.sleep(1) # wait 1s before retry
        
        if gen_resp.status_code == 200:
            answer = gen_resp.output.text
            return {
                "answer": answer,
                "intent": intent,
                "sources": [
                    {"content": row[2], "similarity": float(row[3])} 
                    for row in results
                ]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Generation failed: {gen_resp.message}")

    except Exception as e:
        print(f"Error in ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    print("Starting RAG Service with FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=5001)
