import os
import torch

class Config:
    # ================= 路径配置 (自动计算) =================
    # 获取 src 目录的绝对路径
    SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录 (src 的上一级)
    ROOT_DIR = os.path.dirname(SRC_DIR)
    
    # 数据路径
    DATA_DIR = os.path.join(ROOT_DIR, 'data', 'processed')
    TRAIN_FILE = os.path.join(DATA_DIR, 'train.json')
    VAL_FILE = os.path.join(DATA_DIR, 'val.json')
    TEST_FILE = os.path.join(DATA_DIR, 'test.json') 
    
    # 模型保存路径
    MODEL_SAVE_DIR = os.path.join(ROOT_DIR, 'saved_models', 'bert_multi_task_v1')
    if not os.path.exists(MODEL_SAVE_DIR):
        os.makedirs(MODEL_SAVE_DIR)
    
    # BERT 预训练模型 (会自动下载，也可以改为本地路径)
    BERT_PATH = 'bert-base-chinese'
    
    # ================= 训练参数 =================
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MAX_LEN = 128          # 文本最大长度
    TRAIN_BATCH_SIZE = 32  # 显存不够就改小 
    VALID_BATCH_SIZE = 16
    EPOCHS = 30            # 训练轮数
    LEARNING_RATE = 2e-5   # 学习率
    
    # ================= 业务参数 (8个维度) =================
    # 顺序必须固定！千万不能乱！
    TARGET_COLS = [
        'logistics', 'condition', 'service', 'price', # 服务侧
        'gameplay', 'visuals', 'story', 'audio'       # 游戏侧
    ]
    
    # 标签数量: 0, 1, 2, 3
    NUM_LABELS = 4