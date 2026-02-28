import sys
import os
import re

# 将项目根目录添加到 python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection
from src.config import Config
from dashscope import TextEmbedding
import dashscope

dashscope.api_key = Config.DASHSCOPE_API_KEY

def parse_rules_txt(file_path):
    """
    解析 Txt 文件，提取 Q&A 块
    返回列表: [{'question': '...', 'answer': '...'}, ...]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 简单拆分逻辑：按 "Q:" 切分
    # 格式:
    # Q: 问题标题
    # A: 回答内容...
    
    rules = []
    # 使用正则匹配 Q 和 A
    # pattern 解释:
    # Q:\s*(.*?)\n       -> 匹配 Q: 后面的问题文本 (group 1)
    # \s*A:\s*           -> 匹配 A: 标记
    # (.*?)              -> 匹配回答内容 (group 2, dotall模式)
    # (?=\nQ:|\Z)        -> 这里用前瞻，直到下一个Q开始或文件结束
    pattern = re.compile(r'Q:\s*(.*?)\n\s*A:\s*(.*?)(?=\nQ:|\Z)', re.DOTALL)
    
    matches = pattern.findall(content)
    
    for q, a in matches:
        rules.append({
            "question": q.strip(),
            "answer": a.strip()
        })
    
    return rules

def init_platform_rules():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platform_rules.txt")
    
    if not os.path.exists(file_path):
        print(f"❌ 找不到规则文件: {file_path}")
        return

    print(f"📖 读取规则文件: {file_path}")
    rules = parse_rules_txt(file_path)
    print(f"� 解析出 {len(rules)} 条规则，准备入库...")
    
    if not rules:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    
    # 可选：先清空旧的规则 (category='rule')，防止重复堆积
    cur.execute("DELETE FROM documents WHERE category = 'rule'")
    print("🗑️  已清空旧的规则数据")

    count = 0
    try:
        for rule in rules:
            print(f"处理: {rule['question']}...")
            
            # 1. 构造 Embedding 输入
            # 加上 "平台规则" 上下文
            embedding_input = f"分类：平台规则；问题：{rule['question']}；答案：{rule['answer']}"
            
            # 2. 生成向量
            resp = TextEmbedding.call(
                model=TextEmbedding.Models.text_embedding_v1,
                input=embedding_input
            )
            
            if resp.status_code == 200:
                embedding = resp.output['embeddings'][0]['embedding']
                
                # 3. 构造展示内容
                display_content = f"🛡️规则：{rule['question']}\n\n📝说明：\n{rule['answer']}"
                
                # 4. 存入数据库 (game_id 为 NULL)
                cur.execute(
                    """
                    INSERT INTO documents (game_id, category, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (None, 'rule', display_content, embedding)
                )
                count += 1
            else:
                print(f"❌ Embedding 失败: {resp.message}")
        
        conn.commit()
        print(f"\n✅ 成功导入/更新 {count} 条平台规则！")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 导入出错: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_platform_rules()
