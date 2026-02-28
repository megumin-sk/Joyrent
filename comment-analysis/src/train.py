import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, get_linear_schedule_with_warmup
from tqdm import tqdm
import os

# 导入我们写的模块
from config import Config
from dataset import RentalDataset
from model import MultiHeadBERT
from utils import EarlyStopping

# ================= 损失函数 =================
def loss_fn(outputs, targets):
    class_weights = torch.tensor([6.0, 4.0, 4.0, 1.0]).to(outputs[0].device)
    loss_fct = nn.CrossEntropyLoss(weight=class_weights) 
    # ====================================================
    
    total_loss = 0
    for i, output in enumerate(outputs):
        loss = loss_fct(output, targets[:, i])
        total_loss += loss
        
    return total_loss

# ================= 训练循环 =================
def train_fn(data_loader, model, optimizer, device, scheduler):
    model.train()
    final_loss = 0
    
    loop = tqdm(data_loader, total=len(data_loader), leave=True)
    for data in loop:
        ids = data['ids'].to(device)
        mask = data['mask'].to(device)
        targets = data['targets'].to(device)

        optimizer.zero_grad()
        outputs = model(ids, mask)
        loss = loss_fn(outputs, targets)
        
        # 1. 反向传播计算梯度
        loss.backward()
        
        # 梯度裁剪：如果梯度范数超过 1.0，就把它强行切断。
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        # 2. 更新参数
        optimizer.step()
        scheduler.step()

        final_loss += loss.item()
        loop.set_description(f"Train Loss: {loss.item():.4f}")

    return final_loss / len(data_loader)

# ================= 验证循环 =================
def eval_fn(data_loader, model, device):
    model.eval()
    final_loss = 0
    with torch.no_grad():
        for data in tqdm(data_loader, total=len(data_loader), desc="Validating"):
            ids = data['ids'].to(device)
            mask = data['mask'].to(device)
            targets = data['targets'].to(device)

            outputs = model(ids, mask)
            loss = loss_fn(outputs, targets)
            final_loss += loss.item()
            
    return final_loss / len(data_loader)

# ================= 主入口 =================
if __name__ == "__main__":
    print(f"🚀 Training Config: Device={Config.DEVICE}, Batch={Config.TRAIN_BATCH_SIZE}")
    
    # 1. 准备 Tokenizer
    tokenizer = BertTokenizer.from_pretrained(Config.BERT_PATH)
    
    # 2. 准备 Dataset 和 DataLoader
    train_dataset = RentalDataset(Config.TRAIN_FILE, tokenizer, Config.MAX_LEN, Config.TARGET_COLS)
    val_dataset = RentalDataset(Config.VAL_FILE, tokenizer, Config.MAX_LEN, Config.TARGET_COLS)
    
    train_loader = DataLoader(train_dataset, batch_size=Config.TRAIN_BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=Config.VALID_BATCH_SIZE, shuffle=False)
    
    # 3. 初始化模型
    model = MultiHeadBERT(Config)
    model.to(Config.DEVICE)
    
    # 4. 优化器与调度器
    optimizer = AdamW(model.parameters(), lr=Config.LEARNING_RATE)
    total_steps = len(train_loader) * Config.EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=0, num_training_steps=total_steps
    )
    
    # 5. 早停机制 (模型保存路径)
    save_path = os.path.join(Config.MODEL_SAVE_DIR, "best_model.bin")
    early_stopping = EarlyStopping(patience=3, path=save_path)
    
    # 6. 开始 Epoch 循环
    for epoch in range(Config.EPOCHS):
        print(f"\n======== Epoch {epoch + 1}/{Config.EPOCHS} ========")
        
        train_loss = train_fn(train_loader, model, optimizer, Config.DEVICE, scheduler)
        val_loss = eval_fn(val_loader, model, Config.DEVICE)
        
        print(f"📈 Avg Train Loss: {train_loss:.4f}")
        print(f"📉 Avg Valid Loss: {val_loss:.4f}")
        
        # 检查是否需要早停或保存模型
        early_stopping(val_loss, model)
        if early_stopping.early_stop:
            print("⚠️ Early stopping triggered!")
            break

    print("🎉 训练完成！最佳模型已保存。")