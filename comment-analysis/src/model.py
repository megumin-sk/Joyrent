import torch.nn as nn
from transformers import BertModel

class MultiHeadBERT(nn.Module):
    def __init__(self, config):
        super(MultiHeadBERT, self).__init__()
        # 加载预训练模型
        self.bert = BertModel.from_pretrained(config.BERT_PATH)
        self.drop = nn.Dropout(0.3)
        
        # 定义 8 个独立的分类头
        # nn.ModuleList 类似 List，但会被 PyTorch 自动识别为子模块
        self.heads = nn.ModuleList([
            nn.Linear(768, config.NUM_LABELS) for _ in range(len(config.TARGET_COLS))
        ])

    def forward(self, ids, mask):
        # BERT 输出
        output = self.bert(ids, attention_mask=mask)
        
        # 使用 pooler_output (代表整个句子的向量, shape: [batch, 768])
        pooled_output = self.drop(output.pooler_output)
        
        # 让 8 个头分别进行预测
        # 返回一个列表，包含 8 个 Tensor
        logits_list = [head(pooled_output) for head in self.heads]
        
        return logits_list