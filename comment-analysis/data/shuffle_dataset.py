import json
import random
import os

# ================= 配置区域 =================
# 你指定的目标文件路径
TARGET_FILE = r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\svm_train.json'

# 随机种子 (修改这个数字可以改变打乱的顺序)
SEED = 2025
# ===========================================

def shuffle_json_file():
    print(f"📂 正在读取文件: {TARGET_FILE}")
    
    if not os.path.exists(TARGET_FILE):
        print("❌ 错误：找不到文件，请检查路径。")
        return

    # 1. 读取数据
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("❌ 错误：JSON 内容不是一个列表 (List)，无法打乱。")
        return

    print(f"📊 数据总量: {len(data)} 条")
    
    # 打印前第一条数据做对比
    print(f"   [打乱前第1条]: {str(data[0])[:50]}...")

    # 2. 随机打乱
    print("🔀 正在执行随机打乱 (Shuffle)...")
    random.seed(SEED)
    random.shuffle(data)

    # 打印打乱后的第一条数据
    print(f"   [打乱后第1条]: {str(data[0])[:50]}...")

    # 3. 覆盖保存
    print("💾 正在保存回原文件...")
    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("✅ 打乱完成！文件已更新。")

if __name__ == "__main__":
    shuffle_json_file()