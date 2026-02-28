import json
import os

# ================= 配置区域 =================
# 这里填你所有需要检查的文件路径
# 建议检查处理后的三个文件，看看有没有重叠
FILE_PATHS = {
    'train': r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\train.json',
    'val':   r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\val.json',
    'test':  r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\test.json'
}
# ===========================================

def load_texts(file_path):
    """读取文件并提取所有文本"""
    if not os.path.exists(file_path):
        print(f"⚠️ 文件不存在，跳过: {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 返回一个列表，包含 (索引, 文本内容)
    return [(i, item.get('text', '').strip()) for i, item in enumerate(data)]

def check_internal_duplicates(name, texts_with_id):
    """检查单个文件内部的重复"""
    print(f"\n🔍 正在检查文件内部重复: 【{name}】")
    
    seen = {} # map: text -> index
    duplicates = []
    
    for idx, text in texts_with_id:
        if text in seen:
            duplicates.append((seen[text], idx, text))
        else:
            seen[text] = idx
            
    if not duplicates:
        print("   ✅ 干净！无内部重复。")
    else:
        print(f"   🚨 发现 {len(duplicates)} 组重复数据！")
        for orig_idx, curr_idx, text in duplicates[:3]: # 只打印前3个例子
            print(f"      - 索引 {curr_idx} 与索引 {orig_idx} 重复: {text[:30]}...")

    return set([t for _, t in texts_with_id]) # 返回纯文本集合用于跨文件比较

def check_data_leakage(sets_dict):
    """检查跨文件的数据泄露 (Data Leakage)"""
    print(f"\n🕵️ 正在检查数据泄露 (跨文件重复)...")
    
    # 检查 Train vs Test (最严重的泄露)
    if 'train' in sets_dict and 'test' in sets_dict:
        intersection = sets_dict['train'].intersection(sets_dict['test'])
        if intersection:
            print(f"   🚨 严重警告！Train 和 Test 之间有 {len(intersection)} 条重复数据！(模型在作弊)")
            print(f"      示例: {list(intersection)[0][:30]}...")
        else:
            print("   ✅ Train 与 Test 无交集 (安全)。")
            
    # 检查 Train vs Val
    if 'train' in sets_dict and 'val' in sets_dict:
        intersection = sets_dict['train'].intersection(sets_dict['val'])
        if intersection:
            print(f"   ⚠️ 警告：Train 和 Val 之间有 {len(intersection)} 条重复数据。")
        else:
            print("   ✅ Train 与 Val 无交集。")

if __name__ == "__main__":
    print("🚀 开始数据重复性检查...")
    
    # 1. 加载所有数据
    text_sets = {}
    for name, path in FILE_PATHS.items():
        texts = load_texts(path)
        if texts:
            # 2. 检查每个文件内部是否有重复
            unique_texts = check_internal_duplicates(name, texts)
            text_sets[name] = unique_texts
            
    # 3. 检查文件之间是否有重复 (数据泄露)
    check_data_leakage(text_sets)
    
    print("\n完成。如果发现严重泄露，建议重新运行 split_data.py 之前先对原始 dataset.json 进行去重。")