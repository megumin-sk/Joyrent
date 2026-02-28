import os
import torch

class TrainConfig:
    # =========================================================
    # 📂 路径配置
    # =========================================================
    # 项目根目录 (假设当前脚本在 scripts/ 目录下，向上找两级)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 原始预训练模型名称 (使用多语言版 DistilBERT)
    PRETRAINED_MODEL_NAME = "distilbert/distilbert-base-multilingual-cased"
    
    # 训练数据路径
    TRAIN_FILE = os.path.join(BASE_DIR, "data", "processed", "train.csv")
    DEV_FILE = os.path.join(BASE_DIR, "data", "processed", "dev.csv")
    
    # 模型保存输出路径 (训练好的模型会保存在这里)
    OUTPUT_DIR = os.path.join(BASE_DIR, "model", "bert_intent_classifier")
    
    # 日志保存路径 (用于 TensorBoard 查看训练曲线)
    LOG_DIR = os.path.join(BASE_DIR, "logs")

    # =========================================================
    # 🏷️ 标签配置
    # =========================================================
    # 标签与 ID 的映射 (必须与推理时的 Config 保持完全一致)
    LABEL2ID = {
        "rule": 0,
        "game": 1,
        "all": 2
    }
    ID2LABEL = {
        0: "rule",
        1: "game",
        2: "all"
    }
    NUM_LABELS = len(LABEL2ID)

    # =========================================================
    # ⚙️ 训练超参数 (针对小数据集优化)
    # =========================================================
    # 句子最大长度
    # 客服对话通常比较短，128 足够了，设太大会浪费显存和计算时间
    MAX_LEN = 128
    
    # 批次大小 (Batch Size)
    # 如果显存只有 4G-6G，建议设为 8 或 16；如果是 CPU 训练，设为 8
    BATCH_SIZE = 16
    
    # 学习率 (Learning Rate)
    LEARNING_RATE = 2e-5
    
    # 训练轮数 (Epochs)
    EPOCHS = 5
    
    # 权重衰减 (Weight Decay)
    # 防止过拟合
    WEIGHT_DECAY = 0.01
    
    # 预热比例 (Warmup Ratio)
    WARMUP_RATIO = 0.1

    # =========================================================
    # 🖥️ 硬件配置
    # =========================================================
    # 自动检测 GPU
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # 数据加载线程数 (Windows 下建议设为 0，否则容易报错；Linux 可设为 4)
    NUM_WORKERS = 0 if os.name == 'nt' else 4
    
    # 随机种子 (保证每次训练结果可复现)
    SEED = 42

    @staticmethod
    def show_info():
        """打印当前配置信息"""
        print(f"🚀 训练配置已加载:")
        print(f"   - 基础模型: {TrainConfig.PRETRAINED_MODEL_NAME}")
        print(f"   - 设备: {TrainConfig.DEVICE}")
        print(f"   - 类别数: {TrainConfig.NUM_LABELS} {list(TrainConfig.LABEL2ID.keys())}")
        print(f"   - Epochs: {TrainConfig.EPOCHS}")
        print(f"   - Batch Size: {TrainConfig.BATCH_SIZE}")
        print(f"   - 数据路径: {TrainConfig.TRAIN_FILE}")