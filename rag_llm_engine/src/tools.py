from langchain_core.tools import tool
from database import get_db_connection, get_games_stock
from dashscope import MultiModalEmbedding
from config import Config

# 内部辅助函数：负责在 pgvector 中检索内容
def _vector_search(query: str, category: str = None):
    resp = MultiModalEmbedding.call(
        model=Config.EMBEDDING_MODEL,
        input=[{'text': query}]
    )
    if resp.status_code != 200:
        return []
    
    query_vec = resp.output['embeddings'][0]['embedding']
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 构建 SQL，如果传了 category 就加过滤条件
    sql = "SELECT game_id, content FROM documents WHERE 1=1"
    params = []
    
    if category:
        sql += " AND category = %s"
        params.append(category)
        
    sql += f" ORDER BY embedding <=> %s::vector LIMIT {Config.TOP_K}"
    params.append(query_vec)
    
    cur.execute(sql, tuple(params))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

@tool
def search_game_info(query: str) -> str:
    """
    当用户询问游戏内容、攻略、玩法、评价或者询问某个游戏是否有货时调用。
    该工具会返回游戏背景资料以及该游戏的实时库存数量。
    """
    # 1. 检索向量库中的游戏资料
    results = _vector_search(query, category='game')
    if not results:
        return "未找到相关游戏资料。"
    
    # 2. 提取 game_id 并从 MySQL 查询实时库存
    game_ids = [row[0] for row in results if row[0] is not None]
    stock_text = ""
    if game_ids:
        stocks = get_games_stock(list(set(game_ids)))
        stock_text = "\n【实时库存】:\n" + "\n".join(
            [f"《{s['title']}》剩余:{s['available_stock']}份 | 日租金:¥{s['daily_rent_price']} | 押金:¥{s['deposit_price']}" for s in stocks.values()]
        )
    
    context = "\n".join([f"资料片段: {row[1]}" for row in results])
    return f"{context}\n{stock_text}"

@tool
def search_platform_rules(query: str) -> str:
    """
    当用户询问关于租金、押金、退款流程、发货物流、会员权益等平台规则时调用。
    """
    results = _vector_search(query, category='rule')
    if not results:
        return "未找到相关平台规则。"
    
    return "\n".join([f"规则条目: {row[1]}" for row in results])
