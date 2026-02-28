import json
import torch
from torch.utils.data import Dataset

class RentalDataset(Dataset):
    def __init__(self, data_path, tokenizer, max_len, target_cols):
        self.data = self._load_data(data_path)
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.target_cols = target_cols

    def _load_data(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        text = str(item['text'])
        labels_dict = item['labels']

        # 1. 文本 Tokenization
        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_token_type_ids=False
        )

        ids = inputs['input_ids']
        mask = inputs['attention_mask']

        # 2. 标签处理 (读取 Config 定义的8个维度)
        # 如果 JSON 里没有这个维度，默认给 -1
        target_values = [labels_dict.get(col, -1) for col in self.target_cols]

        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'targets': torch.tensor(target_values, dtype=torch.long)
        }