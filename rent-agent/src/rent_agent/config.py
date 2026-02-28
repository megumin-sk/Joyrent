"""
rent-agent 配置管理模块

支持从环境变量读取配置，包括：
- 双模型架构（意图识别小模型 + 回答大模型）
- 向量检索配置
- 数据库连接（PostgreSQL + MySQL）
- Agent 系统提示词
"""
import os
from typing import Optional
from dotenv import load_dotenv, find_dotenv

# 加载 .env 文件中的环境变量
load_dotenv(find_dotenv())

class Config:
    """rent-agent 全局配置类"""
    
    # ==================== API Key ====================
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_BASE_URL: str = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # ==================== 双模型架构 ====================
    # 意图识别小模型（成本优化）
    INTENT_MODEL: str = os.getenv("INTENT_MODEL", "tongyi-xiaomi-analysis-flash")
    INTENT_TEMPERATURE: float = 0.1  # 低温度保证分类稳定性
    
    # 最终回答大模型（性能优先）
    ANSWER_MODEL: str = os.getenv("ANSWER_MODEL", "qwen3.5-plus")
    ANSWER_TEMPERATURE: float = 0.7  # 适中温度保证回答自然
    
    # 向量嵌入模型
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "multimodal-embedding-v1")
    EMBEDDING_DIMENSION: int = 1024
    
    # ==================== PostgreSQL / pgvector ====================
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "rent_agent")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    @property
    def DATABASE_URL(self) -> str:
        """PostgreSQL 连接字符串"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # ==================== MySQL（JoyRent 业务库）====================
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DB: str = os.getenv("MYSQL_DB", "joy_rent")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    
    @property
    def MYSQL_URL(self) -> str:
        """MySQL 连接字符串"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
    
    # ==================== RAG 检索配置 ====================
    TOP_K: int = int(os.getenv("TOP_K", "3"))  # 检索 Top-K 文档
    SIMILARITY_THRESHOLD: float = 0.7  # 相似度阈值
    
    # ==================== Agent 流程控制 ====================
    MAX_CLARIFY_RETRIES: int = 3  # 澄清问题最大重试次数
    MEMORY_WINDOW_SIZE: int = 10  # 对话历史窗口大小
    
    # ==================== 意图分类提示词 ====================
    INTENT_SYSTEM_PROMPT: str = """你是 JoyRent 意图分类器，负责判断用户问题的类型。

【分类规则】
1. **clarify**（需要澄清）：用户问题模糊、信息不足、无法判断意图
   - 示例："有什么推荐吗？"、"这个怎么样？"
   
2. **rule**（平台规则）：询问租赁流程、退款政策、运费标准等平台规则
   - 示例："怎么退押金？"、"运费怎么算？"、"租期可以延长吗？"
   
3. **game**（游戏信息）：询问游戏玩法、评价、库存、价格等
   - 示例："塞尔达好玩吗？"、"有马里奥吗？"、"这个游戏多少钱？"
   
4. **order**（订单查询）：查询订单状态、物流信息等
   - 示例："我的订单到哪了？"、"订单号 123 的状态？"

【输出格式】
严格返回如下 JSON，不要有任何其他文字：
{"category": "分类结果", "confidence": 置信度数值}

其中：
- category: 只能是 clarify / rule / game / order 之一
- confidence: 0.0 到 1.0 之间的小数，表示你对分类结果的确信程度

示例输出：
{"category": "game", "confidence": 0.95}
{"category": "clarify", "confidence": 0.4}"""

    # ==================== 回答生成提示词 ====================
    ANSWER_SYSTEM_PROMPT: str = """你是 JoyRent 游戏租赁平台的客服小助手，负责帮助用户了解游戏信息和平台规则。

【工作原则】
1. **真诚第一**：只告诉用户你确实知道的信息（来自工具检索结果），不知道的就坦诚说"这个我需要再确认一下"或"抱歉，暂时没查到相关资料哦"。
2. **主动查询**：
   - 用户问游戏相关的（玩法、评价、有没有货等）→ 基于 IGDB API 和本地库存数据回答
   - 用户问平台规则（怎么退款、运费多少等）→ 基于检索到的规则文档回答
   - 用户问订单信息 → 基于订单查询结果回答
3. **自然交流**：像朋友聊天一样回答，别太生硬，但也别废话太多。

【回答风格】
- 把检索到的内容用自然的语言转述给用户
- 如果有库存信息，记得告诉用户还剩多少份
- 语气轻松亲切，但保持专业

【重要提醒】
❌ 千万别猜！没查到的信息不要自己编
❌ 不要根据游戏名字就自己脑补游戏内容
❌ 库存数字必须来自工具返回，不能瞎说
❌ 平台规则也不能凭感觉回答

【回答示例】
✅ "我帮您查了一下，《塞尔达传说》目前还有 5 份库存哦！这款游戏..."（基于工具返回）
✅ "关于退押金的流程，根据平台规定..."（引用检索到的规则）
❌ "塞尔达是任天堂的经典游戏..."（这是自己的知识，不是工具返回的）"""

    # ==================== 澄清问题提示词 ====================
    CLARIFY_SYSTEM_PROMPT: str = """你是 JoyRent 客服助手，用户的问题不够明确，需要你引导用户补充信息。

【澄清策略】
1. 如果用户只说"有什么推荐"，问他喜欢什么类型的游戏
2. 如果用户问"这个怎么样"，问他指的是哪个游戏
3. 如果用户问"多少钱"，问他想租哪个游戏

【回答风格】
- 简短友好，不要长篇大论
- 给出 2-3 个选项帮助用户选择
- 示例："您是想了解游戏推荐，还是查询订单呢？😊"
"""

    # ==================== IGDB API 配置 ====================
    IGDB_CLIENT_ID: str = os.getenv("IGDB_CLIENT_ID", "")
    IGDB_CLIENT_SECRET: str = os.getenv("IGDB_CLIENT_SECRET", "")
    IGDB_BASE_URL: str = "https://api.igdb.com/v4"
    IGDB_TIMEOUT: int = 10  # 秒
    IGDB_ACCESS_TOKEN: str = ""  # 运行时动态获取
    
    # ==================== 缓存配置 ====================
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = 0
    CACHE_TTL_GAME_INFO: int = 86400  # 游戏信息缓存 24 小时
    CACHE_TTL_RULES: int = 3600  # 规则缓存 1 小时
    CACHE_TTL_IGDB_TOKEN: int = 5184000  # IGDB Token 缓存 60 天


# 全局配置实例
config = Config()

