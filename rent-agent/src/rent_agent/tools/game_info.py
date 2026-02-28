"""
游戏信息查询工具 (Game Info Tool)

模块架构：
1. IGDBClient: 负责调用 IGDB API
2. LLMHelper: 负责调用 LLM 进行翻译和验证
3. GameDatabase: 负责所有 MySQL 数据库操作（缓存、库存）
4. GameInfoTool: 核心业务逻辑控制器，协调上述组件

Note: LangGraph 节点入口已迁移至 nodes/game_info.py
"""
import json
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

import httpx
import pymysql
from openai import OpenAI

from rent_agent.config import config
from rent_agent.state import get_last_user_message

if TYPE_CHECKING:
    from rent_agent.state import AgentState

logger = logging.getLogger(__name__)


# ============================================================
#  1. IGDB API 客户端
# ============================================================

class IGDBClient:
    """IGDB API 客户端"""

    def __init__(self):
        self.client_id = config.IGDB_CLIENT_ID
        self.client_secret = config.IGDB_CLIENT_SECRET
        self.base_url = config.IGDB_BASE_URL
        self._access_token: Optional[str] = None

    def _get_token(self) -> str:
        """获取 OAuth2 Token"""
        if self._access_token:
            return self._access_token

        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        try:
            resp = httpx.post(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self._access_token = data["access_token"]
            return self._access_token
        except Exception as e:
            logger.error(f"IGDB Token 获取失败: {e}")
            raise

    def search_games(self, keyword: str, limit: int = 3) -> List[Dict]:
        """搜索游戏"""
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self._get_token()}",
        }
        
        # 查询语法：搜索 + 字段选择
        body = (
            f'search "{keyword}";'
            f"fields name, rating, summary, cover.url, "
            f"platforms.name, genres.name, first_release_date;"
            f"limit {limit};"
        )

        try:
            resp = httpx.post(
                f"{self.base_url}/games",
                headers=headers,
                data=body,
                timeout=config.IGDB_TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"IGDB 搜索异常 ({keyword}): {e}")
            return []


# ============================================================
#  2. LLM 辅助类
# ============================================================

class LLMHelper:
    """LLM 辅助功能：翻译与验证"""

    def __init__(self):
        self.client = OpenAI(
            api_key=config.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def _call(self, prompt: str) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=config.INTENT_MODEL,  # 使用小模型
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            return ""

    def generate_keywords(self, user_input: str) -> List[str]:
        """将用户输入转换为 2-3 个英文搜索关键词"""
        prompt = f"""你是一个游戏名称翻译专家。
用户输入："{user_input}"
请返回 2-3 个最可能的英文官方游戏名称，用逗号分隔。
只返回关键词，不要有其他内容。"""
        
        result = self._call(prompt)
        keywords = [k.strip() for k in result.split(",") if k.strip()]
        logger.info(f"LLM 关键词: {user_input} -> {keywords}")
        return keywords or [user_input]

    def verify_and_translate(self, user_input: str, candidates: List[Dict]) -> Optional[Dict]:
        """
        从候选中选出最匹配的游戏，并顺便翻译其简介
        返回格式: {"game": 原始游戏对象, "translated_summary": 中文简介}
        """
        if not candidates:
            return None
        
        # 单个候选直接处理
        if len(candidates) == 1:
            game = candidates[0]
            summary = game.get('summary', '')
            if summary:
                translated = self._translate_summary(summary, game.get('name', ''))
                # 对于单个候选，尝试再单独请求一次中文名（这里简化处理，直接用用户输入或者再次询问大模型）
                # 为了保持接口统一，我们可以复用用户输入作为默认中文名，或者调用一个新的专门翻译名字的方法
                prompt_name = f"将游戏 '{game.get('name', '')}' 翻译为最常用的官方中文名，仅返回名称："
                zh_name = self._call(prompt_name)
                return {"game": game, "translated_summary": translated, "official_chinese_name": zh_name or user_input}
            return {"game": game, "translated_summary": "", "official_chinese_name": user_input}

        # 多个候选：构建候选列表描述
        desc_lines = []
        for i, c in enumerate(candidates):
            name = c.get('name', '')
            rating = c.get('rating', 0)
            summary = c.get('summary', '')[:150] + "..." if c.get('summary') else "无简介"
            desc_lines.append(f"{i+1}. {name} (评分:{rating:.0f})\n   简介: {summary}")
        
        desc = "\n\n".join(desc_lines)

        # 合并提示词：匹配 + 翻译
        prompt = f"""你是游戏信息专家。用户搜索："{user_input}"

候选游戏列表：
{desc}

请完成以下任务：
1. 判断哪一个游戏最匹配用户的搜索（如果都不匹配返回 0）
2. 如果有匹配的，将该游戏的英文简介翻译成地道、专业的中文
3. 如果有匹配的，给出该游戏在国内最常用的官方中文名称

要求：
- 翻译要符合中文表达习惯，保留游戏术语准确性
- 只返回 JSON 格式，不要有其他内容

返回格式：
{{"match_index": 1, "official_chinese_name": "官方中文名称...", "translated_summary": "翻译后的中文简介..."}}

如果都不匹配，返回：
{{"match_index": 0, "official_chinese_name": "", "translated_summary": ""}}"""

        result = self._call(prompt)
        
        # 尝试解析 JSON
        try:
            # 提取 JSON（可能被包裹在 markdown 代码块中）
            json_match = re.search(r'\{[^{}]*"match_index"[^{}]*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                idx = data.get("match_index", 0)
                
                if 0 < idx <= len(candidates):
                    chosen = candidates[idx - 1]
                    translated = data.get("translated_summary", "")
                    zh_name = data.get("official_chinese_name", user_input)
                    logger.info(f"LLM 选中并翻译: #{idx} {chosen.get('name')} -> {zh_name}")
                    return {"game": chosen, "translated_summary": translated, "official_chinese_name": zh_name}
        except Exception as e:
            logger.error(f"JSON 解析失败，尝试回退逻辑: {e}")
            # 回退：尝试提取数字
            match = re.search(r"(\d+)", result)
            if match:
                idx = int(match.group(1))
                if 0 < idx <= len(candidates):
                    chosen = candidates[idx - 1]
                    # 单独翻译
                    summary = chosen.get('summary', '')
                    translated = self._translate_summary(summary, chosen.get('name', '')) if summary else ""
                    prompt_name = f"将游戏 '{chosen.get('name', '')}' 翻译为最常用的官方中文名，仅返回名称："
                    zh_name = self._call(prompt_name)
                    return {"game": chosen, "translated_summary": translated, "official_chinese_name": zh_name or user_input}
        
        return None
    
    def _translate_summary(self, summary: str, game_name: str) -> str:
        """独立翻译方法（作为回退方案）"""
        if not summary:
            return ""
        
        prompt = f"""请将以下关于游戏《{game_name}》的英文简介翻译成专业、流畅的中文：

{summary}

要求：
1. 符合中文表达习惯，避免翻译腔
2. 保留游戏术语的准确性
3. 只返回翻译后的中文内容"""
        
        return self._call(prompt)


# ============================================================
#  3. 数据库封装类
# ============================================================

class GameDatabase:
    """封装 MySQL 中与游戏相关的操作"""

    def _connect(self):
        return pymysql.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def get_cache(self, name: str) -> Optional[Dict]:
        """查询本地缓存 (igdb_game_cache)"""
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                # 3层查询：精确 -> 全文 -> 模糊
                queries = [
                    ("SELECT * FROM igdb_game_cache WHERE name = %s OR chinese_name = %s LIMIT 1", (name, name)),
                    ("SELECT * FROM igdb_game_cache WHERE MATCH(name, chinese_name) AGAINST(%s IN NATURAL LANGUAGE MODE) LIMIT 1", (name,)),
                    ("SELECT * FROM igdb_game_cache WHERE name LIKE %s OR chinese_name LIKE %s LIMIT 1", (f"{name}%", f"{name}%"))
                ]
                
                for sql, params in queries:
                    cursor.execute(sql, params)
                    res = cursor.fetchone()
                    if res:
                        # 格式化 JSON 字段
                        if res.get("platforms"): res["platforms"] = json.loads(res["platforms"])
                        if res.get("genres"): res["genres"] = json.loads(res["genres"])
                        # 格式化评分
                        if res.get("rating"): res["rating"] = float(res["rating"])
                        return res
            return None
        finally:
            conn.close()

    def save_cache(self, game: Dict, chinese_name: Optional[str] = None):
        """写入缓存 (igdb_game_cache)"""
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO igdb_game_cache 
                    (igdb_id, name, chinese_name, summary, rating, cover_url, platforms, genres, first_release_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        summary=VALUES(summary), rating=VALUES(rating), 
                        cover_url=VALUES(cover_url), platforms=VALUES(platforms),
                        chinese_name=COALESCE(chinese_name, VALUES(chinese_name))
                """
                cursor.execute(sql, (
                    game["igdb_id"], game["name"], chinese_name,
                    game.get("summary"), game.get("rating"), game.get("cover_url"),
                    json.dumps(game.get("platforms", []), ensure_ascii=False),
                    json.dumps(game.get("genres", []), ensure_ascii=False),
                    datetime.fromtimestamp(game["first_release_date"]) if game.get("first_release_date") else None
                ))
            conn.commit()
            logger.info(f"缓存写入成功: {game['name']}")
        except Exception as e:
            logger.error(f"缓存写入失败: {e}")
        finally:
            conn.close()

    def get_inventory(self, igdb_id: int, game_name_cn: str = None) -> Optional[Dict]:
        """
        查询库存 (games)，包含自动回填 igdb_id 逻辑
        """
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                # 1. 尝试 igdb_id 精确查找
                cursor.execute(
                    "SELECT id, title, daily_rent_price, available_stock, status "
                    "FROM games WHERE igdb_id = %s AND status = 1", (igdb_id,)
                )
                res = cursor.fetchone()
                if res: return res

                # 2. 尝试中文名模糊匹配 (用于自动关联)
                if game_name_cn:
                    clean_name = game_name_cn.replace("我想租", "").replace("有没有", "").strip()
                    if len(clean_name) >= 2:
                        cursor.execute(
                            "SELECT * FROM games WHERE title LIKE %s AND status = 1 LIMIT 1",
                            (f"%{clean_name}%",)
                        )
                        match = cursor.fetchone()
                        
                        # 3. 自动回填关联
                        if match and not match["igdb_id"]:
                            cursor.execute("UPDATE games SET igdb_id = %s WHERE id = %s", (igdb_id, match["id"]))
                            conn.commit()
                            logger.info(f"自动关联成功: {match['title']} <-> {igdb_id}")
                            return match
            return None
        finally:
            conn.close()


# ============================================================
#  4. 核心工具类 Logic
# ============================================================

class GameInfoTool:
    """游戏信息查询工具 (Facade)"""

    def __init__(self):
        self.igdb = IGDBClient()
        self.llm = LLMHelper()
        self.db = GameDatabase()

    def _format_game(self, raw: Dict) -> Dict:
        """格式化 IGDB 原始数据"""
        cover = f"https:{raw['cover']['url']}" if raw.get("cover") else None
        return {
            "igdb_id": raw["id"],
            "name": raw.get("name", ""),
            "rating": round(raw.get("rating", 0), 1),
            "summary": raw.get("summary", ""),
            "cover_url": cover,
            "platforms": [p["name"] for p in raw.get("platforms", [])],
            "genres": [g["name"] for g in raw.get("genres", [])],
            "first_release_date": raw.get("first_release_date"),
        }

    def search(self, user_input: str) -> Dict[str, Any]:
        """
        执行完整搜索流程：
        缓存 -> LLM翻译关键词 -> IGDB搜索 -> LLM验证+翻译 -> 存缓存 -> 查库存
        """
        logger.info(f"开始搜索游戏: {user_input}")
        
        # 1. 查缓存
        cached = self.db.get_cache(user_input)
        if cached:
            inventory = self.db.get_inventory(cached["igdb_id"], user_input)
            return {"game_info": cached, "inventory": inventory, "source": "cache", "status": "success"}

        # 2. LLM 生成关键词
        keywords = self.llm.generate_keywords(user_input)
        
        # 3. IGDB 搜索候选 (取并集)
        candidates = []
        seen = set()
        for kw in keywords:
            for game in self.igdb.search_games(kw):
                if game["id"] not in seen:
                    candidates.append(game)
                    seen.add(game["id"])
        
        # 4. LLM 验证最佳匹配 + 翻译（合并调用）
        match_result = self.llm.verify_and_translate(user_input, candidates)
        
        if not match_result:
            return {"game_info": None, "inventory": None, "source": "igdb", "status": "not_found"}

        # 5. 格式化游戏信息
        best_match = match_result["game"]
        game_info = self._format_game(best_match)
        
        # 6. 使用翻译后的中文简介替换原始英文
        translated_summary = match_result.get("translated_summary", "")
        if translated_summary:
            game_info["summary"] = translated_summary
            logger.info(f"已使用中文简介替换原始英文")
        
        # 提取官方中文名称，如果没有则回退到 user_input
        official_chinese_name = match_result.get("official_chinese_name", user_input)
        if not official_chinese_name:
            official_chinese_name = user_input
        
        # 7. 存入缓存（此时存的是中文简介和官方中文名称）
        self.db.save_cache(game_info, chinese_name=official_chinese_name)
        
        # 8. 查库存 (库存表也优先用官方中文名去模糊匹配)
        inventory = self.db.get_inventory(game_info["igdb_id"], official_chinese_name)
        
        return {"game_info": game_info, "inventory": inventory, "source": "igdb", "status": "success"}
