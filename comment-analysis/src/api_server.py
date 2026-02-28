from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from analysis_service import ContentSecuritySystem
import uvicorn

app = FastAPI(title="JoyRent Comment Analysis API")

# 全局初始化，避免每次请求都加载权重
security_system = ContentSecuritySystem()

class CommentRequest(BaseModel):
    text: str

@app.post("/api/comment/analyze")
async def analyze_comment(request: CommentRequest):
    """
    接收评论文本，执行 SVM 过滤和 BERT 细粒度情感分析。
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="评论内容不能为空")
    
    try:
        result = security_system.process_comment(request.text)
        return {
            "code": 200,
            "msg": "success",
            "result": result
        }
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # 启动服务，监听 5002 端口
    uvicorn.run(app, host="0.0.0.0", port=5002)
