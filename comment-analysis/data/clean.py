import json
import os

# ================= 配置区域 =================
# 注意：你需要将这里的路径改为你正在训练的文件路径 (例如 train.json)
# 修复成功后，建议也对 val.json 和 test.json 运行一遍
FILE_TO_FIX = r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\test.json'

# 8个维度列表 (用于遍历)
TARGET_COLS = [
    'logistics', 'condition', 'service', 'price', 
    'gameplay', 'visuals', 'story', 'audio'
]
# ===========================================

def fix_labels_in_file(file_path):
    print(f"🛠️ 正在读取并尝试修复文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 找不到文件: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 文件加载失败: {e}")
        return
    
    fix_count = 0
    
    for idx, item in enumerate(data):
        labels_dict = item.get('labels', {})
        
        for col in TARGET_COLS:
            val = labels_dict.get(col)
            
            # 检查是否为不合法的 -2
            if val == -2:
                # 核心修复逻辑：将 -2 替换为 -1 (忽略)
                item['labels'][col] = -1
                fix_count += 1
                
                # 打印修复信息 (可选，但有助于确认)
                # print(f"  修复 #{fix_count}: 索引 {idx}, 维度 {col}，已从 -2 替换为 -1")

    # 重新保存文件
    if fix_count > 0:
        print("-" * 50)
        print(f"✅ 修复成功！在 {len(data)} 条数据中，共替换了 {fix_count} 处不合法的 -2 标签。")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"💾 修复后的文件已覆盖保存至: {file_path}")
    else:
        print("🎉 文件中未发现不合法的 -2 标签，无需修复。")


if __name__ == "__main__":
    # 修复 train.json
    fix_labels_in_file(FILE_TO_FIX)
    
    # 建议手动运行：
    # fix_labels_in_file(r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\val.json')