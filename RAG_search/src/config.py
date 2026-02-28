import os
import torch

class Config:
    # 基础路径 (可选，方便管理)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 阿里云 DashScope 配置
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    
    # 数据库配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "root")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    
    # 指向训练好的 RAG_Intend_Bert 模型目录
    BERT_MODEL_PATH = "d:\\workspace\\JoyRent\\SwitchRent\\RAG_Intend_Bert\\model\\bert_intent_classifier"
    
    # 意图标签映射
    BERT_LABEL_MAP = {
        0: "rule",  # 平台规则
        1: "game",  # 游戏内容
        2: "all"    # 混合意图
    }
    
    # 设备配置 (自动检测)
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # ---------------------------------------------------------
    # 🔍 RAG 检索配置
    # ---------------------------------------------------------
    EMBEDDING_DIMENSION = 1536
    TOP_K = 3
    
    # 检索阈值 (可选：低于此分数的检索结果即使搜到了也被丢弃，防止幻觉)
    SIMILARITY_THRESHOLD = 0.6 

    # ---------------------------------------------------------
    # 🗣️ LLM 回答生成配置
    # ---------------------------------------------------------
    # 针对混合场景进行了微调，明确告知 LLM 可能收到不同来源的资料
    RAG_ANSWER_PROMPT = """
    你是一个专业的 Switch 游戏租赁平台客服助手 (JoyRent AI)。
    请根据以下【参考资料】来回答用户的【问题】。
    
    注意：
    1. 【参考资料】可能包含“平台规则”和“游戏攻略”两方面的信息，请综合整理，完整回答用户的疑问。
    2. 回答要语气亲切、专业、条理清晰。
    3. 如果用户同时问了两个问题（如押金和攻略），请分点作答。
    4. 如果参考资料里没有提到的信息，请诚实回答“资料中未提及相关信息”，不要胡编乱造。
    5. ❗【非常重要】如果参考资料中包含【实时库存信息】，请务必在回答中明确告知用户当前库存数量！不要忽略！
    
    【参考资料】：
    {context}
    
    【用户问题】：
    {query}
    
    请生成回答：
    """