import json
import random
import os

# ================= 配置区域 =================
# 数据文件夹路径
DATA_DIR = r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed'

# 要合并的三个文件名
FILES = ['train.json', 'val.json', 'test.json']

# 重新划分的比例
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
# 剩下的 0.1 给测试集

# 随机种子 (修改这个数字可以改变洗牌的结果)
SEED = 2025 
# ===========================================

def reshuffle():
    all_data = []
    
    print("🔄 开始合并现有数据集...")
    
    # 1. 合并 (Merge)
    for filename in FILES:
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.extend(data)
                print(f"   - 已加载 {filename}: {len(data)} 条")
        else:
            print(f"   ⚠️ 警告: 找不到文件 {filename}，跳过")

    total_count = len(all_data)
    print(f"📊 数据总量: {total_count} 条")

    if total_count == 0:
        print("❌ 没有数据，终止操作。")
        return

    # 2. 打乱 (Shuffle)
    random.seed(SEED)
    random.shuffle(all_data)
    print("🔀 数据已打乱 (Shuffle Complete)")

    # 3. 切分 (Split)
    train_end = int(total_count * TRAIN_RATIO)
    val_end = int(total_count * (TRAIN_RATIO + VAL_RATIO))

    new_train = all_data[:train_end]
    new_val = all_data[train_end:val_end]
    new_test = all_data[val_end:]

    # 4. 保存 (Save)
    print("💾 正在重新分配并保存...")
    
    def save_file(filename, data):
        path = os.path.join(DATA_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   - {filename}: {len(data)} 条")

    save_file('train.json', new_train)
    save_file('val.json', new_val)
    save_file('test.json', new_test)

    print("-" * 30)
    print("🎉 重组完成！所有的‘补丁数据’现在已经均匀分散了。")
    print("👉 请重新运行 src/train.py 开始新的训练。")

if __name__ == "__main__":
    reshuffle()