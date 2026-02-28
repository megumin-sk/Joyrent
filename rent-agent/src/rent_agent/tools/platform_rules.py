"""
平台规则检索工具 (Platform Rules Tool)

模块架构：
1. EmbeddingHelper: 调用 LLM (DashScope/OpenAI) 生成文本向量
2. RuleDatabase: 封装 PostgreSQL + pgvector 的向量检索操作
3. PlatformRulesTool: 核心逻辑，协调 Embedding 和 数据库检索

Note: LangGraph 节点入口已迁移至 nodes/platform_rules.py
"""
import logging
import json
from typing import List, Dict, Any, Optional, TYPE_CHECKING

# Project-specific imports
from rent_agent.config import config
from rent_agent.state import get_last_user_message

# Conditional import for AgentState to avoid circular dependencies
if TYPE_CHECKING:
    from rent_agent.state import AgentState

# Initialize logger
logger = logging.getLogger(__name__)

# Third-party library imports
import dashscope
import psycopg2
from pgvector.psycopg2 import register_vector


# ============================================================
#  1. Embedding 辅助类 (DashScope Native)
# ============================================================

class EmbeddingHelper:
    """负责将文本转换为向量"""

    def __init__(self):
        dashscope.api_key = config.DASHSCOPE_API_KEY
        self.model = config.EMBEDDING_MODEL

    def get_embedding(self, text: str) -> List[float]:
        """获取文本的 Embedding 向量"""
        try:
            # 移除换行符
            text = text.replace("\n", " ")
            
            # 使用 DashScope 原生 SDK 调用
            resp = dashscope.MultiModalEmbedding.call(
                model=self.model,
                input=[{'text': text}]
            )
            
            if resp.status_code == 200:
                # DashScope MultiModalEmbedding 返回结构: output['embeddings'][0]['embedding']
                return resp.output['embeddings'][0]['embedding']
            else:
                logger.error(f"DashScope Embedding 调用失败: {resp.message}")
                return []
                
        except Exception as e:
            logger.error(f"Embedding 生成失败: {e}")
            return []


# ============================================================
#  2. 数据库封装类 (PostgreSQL)
# ============================================================

class RuleDatabase:
    """封装 PostgreSQL (pgvector) 操作"""

    def _connect(self):
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        # 必须注册 vector 适配器
        register_vector(conn)
        return conn

    def search_similar(self, embedding: List[float], limit: int = 3, threshold: float = 0.5) -> List[Dict]:
        """
        基于向量相似度检索规则
        忽略 category 和 game_id 字段
        """
        if not embedding:
            return []

        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                # 使用余弦距离 (cosine distance) <=> 1 - cosine similarity
                # operator: <=>
                # 假设表名为 documents
                sql = """
                    SELECT content, 1 - (embedding <=> %s::vector) as similarity
                    FROM documents
                    WHERE 1 - (embedding <=> %s::vector) > %s
                    ORDER BY similarity DESC
                    LIMIT %s
                """
                cursor.execute(sql, (embedding, embedding, threshold, limit))
                results = cursor.fetchall()
                
                # 格式化返回
                return [
                    {"content": row[0], "similarity": float(row[1])}
                    for row in results
                ]
        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            return []
        finally:
            conn.close()

    def add_rule(self, content: str, embedding: List[float]):
        """(辅助方法) 添加规则到数据库"""
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO documents (content, embedding)
                    VALUES (%s, %s)
                """
                cursor.execute(sql, (content, embedding))
            conn.commit()
        finally:
            conn.close()


# ============================================================
#  3. 核心工具类
# ============================================================

class PlatformRulesTool:
    """平台规则检索工具 (Facade)"""

    def __init__(self):
        self.encoder = EmbeddingHelper()
        self.db = RuleDatabase()

    def search(self, query: str) -> List[Dict]:
        """
        根据用户查询检索相关规则
        """
        logger.info(f"开始检索规则: {query}")
        
        # 1. 生成向量
        vector = self.encoder.get_embedding(query)
        if not vector:
            return []
            
        # 2. 数据库检索
        rules = self.db.search_similar(
            vector, 
            limit=config.TOP_K,
            threshold=config.SIMILARITY_THRESHOLD
        )
        
        logger.info(f"检索到 {len(rules)} 条相关规则")
        return rules
