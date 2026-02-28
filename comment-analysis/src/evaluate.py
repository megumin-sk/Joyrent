import torch
import numpy as np
import os
import sys
from tqdm import tqdm
from sklearn.metrics import accuracy_score, f1_score, classification_report
from torch.utils.data import DataLoader
from transformers import BertTokenizer

# 导入项目模块
from config import Config
from model import MultiHeadBERT
from dataset import RentalDataset

# 标签映射 (用于打印报告)
LABEL_NAMES = ["Negative (差)", "Neutral (中)", "Positive (好)", "None (未提及)"]

def evaluate():
    print(f"🚀 开始评估模型...")
    print(f"   设备: {Config.DEVICE}")
    
    # 1. 确定测试集路径
    # 如果 Config 里没定义 TEST_FILE，就手动拼一个
    test_file = getattr(Config, 'TEST_FILE', os.path.join(Config.DATA_DIR, 'test.json'))
    
    if not os.path.exists(test_file):
        print(f"❌ 错误：找不到测试集文件 -> {test_file}")
        return

    # 2. 加载数据
    print(f"   加载测试集: {test_file}")
    tokenizer = BertTokenizer.from_pretrained(Config.BERT_PATH)
    test_dataset = RentalDataset(test_file, tokenizer, Config.MAX_LEN, Config.TARGET_COLS)
    # batch_size 可以设大点，因为不需要反向传播，省显存
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    # 3. 加载模型
    model = MultiHeadBERT(Config)
    model_path = os.path.join(Config.MODEL_SAVE_DIR, 'best_model.bin')
    
    if not os.path.exists(model_path):
        print(f"❌ 错误：找不到模型文件 -> {model_path}")
        print("   请先运行 train.py 进行训练！")
        return
        
    model.load_state_dict(torch.load(model_path, map_location=Config.DEVICE))
    model.to(Config.DEVICE)
    model.eval() # 开启评估模式

    # 4. 收集预测结果
    # 存储 8 个维度的真实标签和预测标签
    # 结构: [ [dim0_preds...], [dim1_preds...], ... ]
    all_targets = [[] for _ in range(len(Config.TARGET_COLS))]
    all_preds = [[] for _ in range(len(Config.TARGET_COLS))]

    print("   正在进行推理...")
    with torch.no_grad():
        for data in tqdm(test_loader):
            ids = data['ids'].to(Config.DEVICE)
            mask = data['mask'].to(Config.DEVICE)
            targets = data['targets'].to(Config.DEVICE) # [Batch, 8]

            outputs = model(ids, mask) # List of 8 tensors

            for i, logits in enumerate(outputs):
                # 获取预测类别 (Argmax)
                preds = torch.argmax(logits, dim=1)
                
                # 收集结果 (转回 CPU 存入列表)
                all_targets[i].extend(targets[:, i].cpu().numpy())
                all_preds[i].extend(preds.cpu().numpy())

    # 5. 计算并打印指标
    print("\n" + "="*60)
    print(f"{'维度 (Dimension)':<15} | {'Accuracy':<10} | {'Macro F1':<10}")
    print("-" * 60)
    
    avg_acc = 0
    avg_f1 = 0
    
    # 详细报告存储
    details = []

    for i, col in enumerate(Config.TARGET_COLS):
        y_true = all_targets[i]
        y_pred = all_preds[i]
        
        # 计算基础指标
        acc = accuracy_score(y_true, y_pred)
        # Macro F1: 对所有类别(0,1,2,3)一视同仁求平均，能反映模型在小样本类别上的表现
        f1 = f1_score(y_true, y_pred, average='macro')
        
        avg_acc += acc
        avg_f1 += f1
        
        print(f"{col:<15} | {acc:.4f}     | {f1:.4f}")
        
        # 生成详细分类报告
        report = classification_report(
            y_true, 
            y_pred, 
            labels=[0, 1, 2, 3], 
            target_names=LABEL_NAMES,
            zero_division=0 # 防止除零警告
        )
        details.append((col, report))

    print("-" * 60)
    print(f"{'OVERALL (平均)':<15} | {avg_acc/8:.4f}     | {avg_f1/8:.4f}")
    print("="*60)

    # 6. 打印详细报告 (可选，如果只想看总览可以注释掉)
    print("\n📝 详细分类报告 (按维度):\n")
    for col, report in details:
        print(f"### {col} ###")
        print(report)
        print("-" * 30)

if __name__ == "__main__":
    evaluate()