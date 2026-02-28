import json
import os

# ================= 配置区域 =================
# 这里填你 split_data.py 生成的那三个文件的路径
FILES_TO_CONVERT = [
    r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\train.json',
    r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\val.json',
    r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\test.json'
]

# 8个维度
TARGET_COLS = [
    'logistics', 'condition', 'service', 'price', 
    'gameplay', 'visuals', 'story', 'audio'
]
# ===========================================

def convert_file(file_path):
    print(f"🔄 正在处理文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"   ⚠️ 跳过，文件不存在: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    change_count = 0
    
    for item in data:
        # 确保 labels 字典存在
        if 'labels' not in item:
            item['labels'] = {}
            
        for col in TARGET_COLS:
            # 获取当前值，如果不存在则默认为 -1
            val = item['labels'].get(col, -1)
            
            # 【核心逻辑】将 -1 转换为 3
            if val == -1:
                item['labels'][col] = 3
                change_count += 1
            # 顺便检查一下是否有遗漏的维度，补全它
            elif col not in item['labels']:
                item['labels'][col] = 3
                change_count += 1

    # 保存回原文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"   ✅ 完成！共更新了 {change_count} 个标签值 (-1 -> 3)")

if __name__ == "__main__":
    print("🚀 开始将数据集转换为 4分类模式 (0,1,2,3)...")
    for file in FILES_TO_CONVERT:
        convert_file(file)
    print("\n🎉 所有文件转换完毕！现在 '3' 代表 '未提及'。")