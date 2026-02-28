# IGDB API 集成指南

## 🎮 为什么选择 IGDB？

**IGDB (Internet Game Database)** 是业界最专业的游戏数据库之一，相比 RAWG：

| 特性 | IGDB | RAWG |
|------|------|------|
| **数据完整性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **更新频率** | 实时 | 较慢 |
| **API 稳定性** | 高 | 中 |
| **中文支持** | 较好 | 一般 |
| **免费额度** | 4 req/s | 20,000 req/month |
| **认证方式** | OAuth2 | API Key |

---

## 🔑 获取 IGDB API 凭证

### 步骤 1：创建 Twitch 应用
IGDB 使用 Twitch 账号进行认证。

1. 访问 [Twitch 开发者控制台](https://dev.twitch.tv/console/apps)
2. 点击 **"Register Your Application"**
3. 填写信息：
   - **Name**: `JoyRent Agent`
   - **OAuth Redirect URLs**: `http://localhost`
   - **Category**: `Application Integration`
4. 点击 **"Create"**
5. 记录下：
   - **Client ID**
   - **Client Secret**（点击 "New Secret" 生成）

### 步骤 2：配置环境变量
```bash
# 编辑 .env 文件
IGDB_CLIENT_ID=your_client_id_here
IGDB_CLIENT_SECRET=your_client_secret_here
```

---

## 🔐 认证流程

IGDB 使用 **OAuth2 Client Credentials** 认证：

```python
import httpx

# 1. 获取 Access Token
def get_igdb_token(client_id: str, client_secret: str) -> str:
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    
    response = httpx.post(url, params=params)
    data = response.json()
    
    return data["access_token"]  # 有效期 60 天

# 2. 使用 Token 调用 IGDB API
def search_game(token: str, client_id: str, game_name: str):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {token}"
    }
    
    # IGDB 使用特殊的查询语法（类似 SQL）
    body = f"""
        search "{game_name}";
        fields name, rating, summary, cover.url;
        limit 5;
    """
    
    response = httpx.post(url, headers=headers, data=body)
    return response.json()
```

---

## 📊 IGDB API 查询语法

IGDB 使用独特的查询语法（Apicalypse），类似 SQL：

### 基础查询
```python
# 搜索游戏
body = """
    search "塞尔达传说";
    fields name, rating, summary;
    limit 10;
"""

# 按 ID 查询
body = """
    fields name, rating, summary, cover.url, platforms.name;
    where id = 1942;
"""

# 过滤条件
body = """
    fields name, rating;
    where rating > 80 & platforms = (6);  # 6 = PC
    sort rating desc;
    limit 10;
"""
```

### 常用字段
```python
# 游戏基本信息
fields = [
    "name",              # 游戏名称
    "rating",            # 评分 (0-100)
    "summary",           # 简介
    "storyline",         # 剧情
    "first_release_date", # 发售日期
    "cover.url",         # 封面图
    "screenshots.url",   # 截图
    "platforms.name",    # 平台（PS5, Switch, PC 等）
    "genres.name",       # 类型
    "involved_companies.company.name"  # 开发商/发行商
]
```

---

## 🛠️ 实现示例

### 完整的游戏查询工具
```python
import httpx
from typing import Optional
from rent_agent.config import config

class IGDBClient:
    """IGDB API 客户端"""
    
    def __init__(self):
        self.client_id = config.IGDB_CLIENT_ID
        self.client_secret = config.IGDB_CLIENT_SECRET
        self.base_url = config.IGDB_BASE_URL
        self.access_token: Optional[str] = None
    
    def _get_token(self) -> str:
        """获取 Access Token（缓存 60 天）"""
        if self.access_token:
            return self.access_token
        
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        response = httpx.post(url, params=params, timeout=10)
        data = response.json()
        
        self.access_token = data["access_token"]
        return self.access_token
    
    def search_games(self, query: str, limit: int = 5) -> list[dict]:
        """
        搜索游戏
        
        Args:
            query: 游戏名称
            limit: 返回结果数量
        
        Returns:
            游戏列表
        """
        token = self._get_token()
        
        url = f"{self.base_url}/games"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        
        body = f"""
            search "{query}";
            fields name, rating, summary, cover.url, platforms.name, 
                   first_release_date, genres.name;
            limit {limit};
        """
        
        response = httpx.post(url, headers=headers, data=body, timeout=10)
        return response.json()
    
    def get_game_by_id(self, game_id: int) -> dict:
        """根据 ID 获取游戏详情"""
        token = self._get_token()
        
        url = f"{self.base_url}/games"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        
        body = f"""
            fields name, rating, summary, storyline, cover.url, 
                   screenshots.url, platforms.name, genres.name,
                   involved_companies.company.name, first_release_date;
            where id = {game_id};
        """
        
        response = httpx.post(url, headers=headers, data=body, timeout=10)
        games = response.json()
        return games[0] if games else {}


# 使用示例
client = IGDBClient()

# 搜索游戏
results = client.search_games("塞尔达传说")
print(results[0])
# {
#     "id": 1942,
#     "name": "The Legend of Zelda: Breath of the Wild",
#     "rating": 97.5,
#     "summary": "...",
#     "cover": {"url": "//images.igdb.com/..."},
#     "platforms": [{"name": "Nintendo Switch"}]
# }

# 获取详情
game = client.get_game_by_id(1942)
```

---

## 🎨 数据格式转换

### IGDB 响应格式
```json
{
  "id": 1942,
  "name": "The Legend of Zelda: Breath of the Wild",
  "rating": 97.5,
  "summary": "Step into a world of discovery...",
  "cover": {
    "url": "//images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.jpg"
  },
  "platforms": [
    {"name": "Nintendo Switch"},
    {"name": "Wii U"}
  ],
  "genres": [
    {"name": "Adventure"},
    {"name": "Role-playing (RPG)"}
  ],
  "first_release_date": 1488499200
}
```

### 转换为统一格式
```python
def format_game_info(igdb_data: dict) -> dict:
    """将 IGDB 数据转换为统一格式"""
    return {
        "id": igdb_data.get("id"),
        "name": igdb_data.get("name"),
        "rating": igdb_data.get("rating", 0) / 20,  # 转换为 0-5 分
        "summary": igdb_data.get("summary", ""),
        "cover_url": f"https:{igdb_data['cover']['url']}" if igdb_data.get("cover") else None,
        "platforms": [p["name"] for p in igdb_data.get("platforms", [])],
        "genres": [g["name"] for g in igdb_data.get("genres", [])],
        "release_date": igdb_data.get("first_release_date")
    }
```

---

## 🚀 集成到 rent-agent

### 在 `tools/game_info.py` 中使用
```python
from rent_agent.state import AgentState

def query_game_info(state: AgentState) -> AgentState:
    """查询游戏信息（IGDB）"""
    game_name = state["context"].get("game_name")
    
    try:
        client = IGDBClient()
        results = client.search_games(game_name, limit=1)
        
        if results:
            state["game_info"] = format_game_info(results[0])
            state["route_status"] = "success"
        else:
            state["route_status"] = "failed"
            state["error_message"] = "未找到该游戏"
    
    except Exception as e:
        state["route_status"] = "failed"
        state["error_message"] = f"IGDB API 错误: {str(e)}"
    
    return state
```

---

## 💰 成本和限流

### 免费额度
- **请求限制**: 4 requests/second
- **无月度限制**
- **Token 有效期**: 60 天

### 优化建议
```python
# 1. 缓存 Token（60 天）
# 2. 缓存游戏信息（24 小时）
# 3. 批量查询（一次查多个游戏）

# 批量查询示例
body = """
    fields name, rating, summary;
    where id = (1942, 1943, 1944);
"""
```

---

## 🔍 常见问题

### Q: Token 过期了怎么办？
A: Token 有效期 60 天，过期后重新调用 `_get_token()` 即可。建议用 Redis 缓存。

### Q: 如何搜索中文游戏？
A: IGDB 支持中文搜索，但结果可能不如英文准确。建议同时搜索中英文名。

### Q: 图片 URL 为什么没有协议？
A: IGDB 返回的图片 URL 格式为 `//images.igdb.com/...`，需要手动加上 `https:`。

### Q: 如何获取游戏的多语言名称？
A: 使用 `alternative_names` 字段：
```python
fields name, alternative_names.name;
```

---

## 📚 参考资料

- [IGDB API 官方文档](https://api-docs.igdb.com/)
- [Apicalypse 查询语法](https://api-docs.igdb.com/#apicalypse)
- [Twitch 开发者控制台](https://dev.twitch.tv/console/apps)
- [IGDB 字段列表](https://api-docs.igdb.com/#game)

---

## ✅ 下一步

1. **获取 IGDB 凭证**（Client ID + Secret）
2. **实现 `IGDBClient` 类**（在 `tools/game_info.py`）
3. **添加 Token 缓存**（Redis）
4. **测试游戏查询功能**
