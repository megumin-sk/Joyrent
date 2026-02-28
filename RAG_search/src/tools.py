# 需要：langchain >= 支持 @tool 的版本
from langchain.tools import tool
from src.database import get_games_stock

@tool("order_query", description="Query remaining stock by game_id", return_direct=True)
def order_query_tool(game_id: int) -> str:
    # 参数校验
    if not isinstance(game_id, int) or game_id <= 0:
        return "invalid game_id"
    try:
        stock_map = get_games_stock([game_id]) or {}
        stock = stock_map.get(game_id)
    except Exception:
        return "查询库存失败"
    if not stock:
        return f"未找到 game_id={game_id} 的库存信息。"
    title = stock.get("title", "")
    available = stock.get("available_stock")
    return f"游戏 {title} (id={game_id}) 剩余库存: {available}"