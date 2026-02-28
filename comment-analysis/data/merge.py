import json
import os
import random

# ================= 配置区域 =================
# 1. 正常数据源 (你的 BERT 数据集)
# 这些评论将被标记为 1 (Normal)
NORMAL_FILES = [
    r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\train.json',
    r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\val.json',
    r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\test.json'
]

# 2. 垃圾数据源 (你刚才生成的 150 条)
# 这些评论将被标记为 0 (Spam)
# 假设你把刚才生成的 150 条保存到了这个路径，如果文件名不同请修改
SPAM_FILE = r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\raw\spam.json'

# 3. 输出目标路径 (你指定的位置)
OUTPUT_FILE = r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\svm\svmset.json'

# 标签定义
LABEL_SPAM = 0   # 垃圾
LABEL_NORMAL = 1 # 正常
# ===========================================

def merge_datasets():
    print("🚀 开始合并 SVM 训练数据...")
    
    combined_data = []
    
    # --- 第一步：加载正常数据 ---
    print(f"\n📦 正在读取正常评论 (Label={LABEL_NORMAL})...")
    normal_count = 0
    for file_path in NORMAL_FILES:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    text = item.get('text', '').strip()
                    if text:
                        combined_data.append({
                            "text": text,
                            "label": LABEL_NORMAL
                        })
                        normal_count += 1
            print(f"   - 已加载 {os.path.basename(file_path)}")
        else:
            print(f"   ⚠️ 找不到文件: {file_path}")

    # --- 第二步：加载垃圾数据 ---
    print(f"\n🗑️ 正在读取垃圾评论 (Label={LABEL_SPAM})...")
    spam_count = 0
    if os.path.exists(SPAM_FILE):
        with open(SPAM_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                text = item.get('text', '').strip()
                if text:
                    combined_data.append({
                        "text": text,
                        "label": LABEL_SPAM
                    })
                    spam_count += 1
        print(f"   - 已加载 {os.path.basename(SPAM_FILE)}")
    else:
        print(f"   ❌ 严重警告：找不到垃圾数据文件 {SPAM_FILE}")
        print("   请确保你已经把那 150 条数据保存到了这个位置！")

    # --- 第三步：打乱与保存 ---
    print(f"\n📊 统计信息:")
    print(f"   - 正常数据: {normal_count} 条")
    print(f"   - 垃圾数据: {spam_count} 条")
    print(f"   - 总计: {len(combined_data)} 条")

    print("\n🔀 正在打乱数据顺序...")
    random.seed(42) # 固定种子，保证每次结果一致
    random.shuffle(combined_data)

    # 确保输出目录存在
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"   - 创建目录: {output_dir}")

    print(f"💾 正在保存至: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    print("\n✅ 合并完成！现在你可以用这个文件去训练 SVM 了。")

if __name__ == "__main__":
    merge_datasets()