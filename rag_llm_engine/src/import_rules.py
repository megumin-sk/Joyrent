import sys
import os
import re

# 确保能找到项目模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection
from config import Config
from dashscope import MultiModalEmbedding
import dashscope

# 设置 API Key
dashscope.api_key = Config.DASHSCOPE_API_KEY

def parse_rules(file_path):
    """从 txt 解析 Q: A: 格式的规则"""
    if not os.path.exists(file_path):
        print(f"❌ 找不到文件: {file_path}")
        return []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 Q: 和 A: 块
    pattern = re.compile(r'Q:\s*(.*?)\n\s*A:\s*(.*?)(?=\nQ:|\Z)', re.DOTALL)
    matches = pattern.findall(content)
    
    rules = []
    for q, a in matches:
        rules.append({
            "question": q.strip(),
            "answer": a.strip()
        })
    return rules

def main():
    # 路径定位到 RAG_search/platform_rules.txt
    rules_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "RAG_search", "platform_rules.txt")
    
    print(f"🚀 开始从 {rules_file} 导入规则...")
    rules = parse_rules(rules_file)
    print(f"✅ 解析完成，共 {len(rules)} 条规则")
    
    if not rules:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    
    # 清空旧规则 (category='rule')
    cur.execute("DELETE FROM documents WHERE category = 'rule'")
    print("🗑️ 已清空旧规则数据")

    count = 0
    try:
        for item in rules:
            print(f"正在处理: {item['question'][:20]}...")
            
            # 1. 构造语义文本
            semantic_text = f"平台规则问题：{item['question']}；回答内容：{item['answer']}"
            
            # 2. 调用 1024 维度的多模态向量模型
            resp = MultiModalEmbedding.call(
                model=Config.EMBEDDING_MODEL,
                input=[{'text': semantic_text}]
            )
            
            if resp.status_code == 200:
                vec = resp.output['embeddings'][0]['embedding']
                
                # 3. 构造存储内容（带点装饰，方便 AI 提取）
                content_to_save = f"【 JoyRent 官方规则 】\n问：{item['question']}\n答：{item['answer']}"
                
                # 4. 写入 PostgreSQL (pgvector)
                cur.execute(
                    "INSERT INTO documents (game_id, category, content, embedding) VALUES (%s, %s, %s, %s)",
                    (None, 'rule', content_to_save, vec)
                )
                count += 1
            else:
                print(f"❌ Embedding 失败 ({item['question'][:10]}): {resp.message}")

        conn.commit()
        print(f"\n🎉 成功！共导入 {count} 条规则到向量库。")
        
    except Exception as e:
        conn.rollback()
        print(f"🔥 导入过程中发生错误: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
