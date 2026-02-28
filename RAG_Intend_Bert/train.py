import os
import sys
import numpy as np
import torch
from datasets import load_dataset
from transformers import Trainer, TrainingArguments, DataCollatorWithPadding
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# ------------------------------------------------------------------
# 🔗 路径配置：将项目根目录加入 Python 搜索路径
# ------------------------------------------------------------------
# 假设 train.py 位于项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 导入配置和工厂类
from config.train_config import TrainConfig
from src.model_factory import ModelFactory 
# ------------------------------------------------------------------

def compute_metrics(eval_pred):
    """
    自定义评估函数：计算准确率和 F1 分数
    """
    predictions, labels = eval_pred
    # predictions 是 logits，取最大值的索引作为预测结果
    preds = np.argmax(predictions, axis=1)
    
    # average='weighted' 用于多分类任务，考虑类别不平衡的情况
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='weighted', zero_division=0
    )
    acc = accuracy_score(labels, preds)
    
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def main():
    # 1. 打印配置信息
    TrainConfig.show_info()
    
    # 2. 检查文件路径
    if not os.path.exists(TrainConfig.TRAIN_FILE) or not os.path.exists(TrainConfig.DEV_FILE):
        print("❌ 错误：找不到训练集或验证集 CSV 文件，请先运行数据划分脚本。")
        return

    # ============================================================
    # 🏗️ 阶段一：使用工厂加载组件 (解耦的核心)
    # ============================================================
    print("\n🏭 正在从工厂加载模型组件...")
    
    # A. 获取分词器
    tokenizer = ModelFactory.get_tokenizer(TrainConfig.PRETRAINED_MODEL_NAME)
    
    # B. 获取模型
    model = ModelFactory.get_model(
        model_path=TrainConfig.PRETRAINED_MODEL_NAME,
        num_labels=TrainConfig.NUM_LABELS,
        id2label=TrainConfig.ID2LABEL,
        label2id=TrainConfig.LABEL2ID
    )

    # ============================================================
    # 📂 阶段二：数据加载与预处理 (直接写在训练流程中)
    # ============================================================
    print("\n📂 正在加载并处理数据...")
    data_files = {"train": TrainConfig.TRAIN_FILE, "validation": TrainConfig.DEV_FILE}
    
    # 加载 CSV 数据集
    dataset = load_dataset("csv", data_files=data_files)

    def preprocess_function(examples):
        """将文本转换为 Token ID 和 Attention Mask"""
        tokenized_inputs = tokenizer(
            examples["text"], 
            truncation=True, 
            padding=False, # 使用动态填充，更高效
            max_length=TrainConfig.MAX_LEN
        )
        
        # 将文本标签转换为数字 ID
        tokenized_inputs["labels"] = [TrainConfig.LABEL2ID[label] for label in examples["label"]]
        return tokenized_inputs

    # 应用预处理，并移除原始的 text 和 label 列
    tokenized_datasets = dataset.map(
        preprocess_function, 
        batched=True, 
        remove_columns=["text", "label"]
    )
    
    # ============================================================
    # 🚀 阶段三：配置 Trainer 并开始训练
    # ============================================================
    print("\n⚙️ 正在配置训练参数...")
    training_args = TrainingArguments(
        output_dir=TrainConfig.OUTPUT_DIR,
        num_train_epochs=TrainConfig.EPOCHS,
        per_device_train_batch_size=TrainConfig.BATCH_SIZE,
        per_device_eval_batch_size=TrainConfig.BATCH_SIZE,
        learning_rate=TrainConfig.LEARNING_RATE,
        weight_decay=TrainConfig.WEIGHT_DECAY,
        warmup_ratio=TrainConfig.WARMUP_RATIO,
        
        eval_strategy="epoch", 
        save_strategy="epoch",       
        logging_dir=TrainConfig.LOG_DIR,
        logging_steps=10,           
        load_best_model_at_end=True, 
        metric_for_best_model="f1", # 使用 F1 Score 作为最佳模型标准，因为它比 Accuracy 对类别不平衡更敏感
        save_total_limit=1,         # 只保留最佳模型，节省空间
        
        dataloader_num_workers=TrainConfig.NUM_WORKERS,
        seed=TrainConfig.SEED,
    )

    # 初始化 Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        # DataCollatorWithPadding 可以在批次内部填充到最长句子的长度，而不是MAX_LEN，节省计算
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer), 
        compute_metrics=compute_metrics,
    )

    # 开始训练 
    print("\n🚀 开始训练模型...")
    trainer.train()

    # ============================================================
    # 💾 阶段四：保存最终产出物
    # ============================================================
    print("\n📊 训练已完成，正在进行最终评估...")
    trainer.evaluate()

    print(f"\n💾 正在保存最佳模型到: {TrainConfig.OUTPUT_DIR}")
    trainer.save_model(TrainConfig.OUTPUT_DIR)
    tokenizer.save_pretrained(TrainConfig.OUTPUT_DIR) 
    
    print("\n✅ 训练完成！模型已保存在 output 目录。")

if __name__ == "__main__":
    main()