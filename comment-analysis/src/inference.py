import torch
from transformers import BertTokenizer
from model import MultiHeadBERT
from config import Config

# 映射字典：把数字转回人类能懂的文字
ID2LABEL = {
    0: "😡 差评 (Negative)",
    1: "😐 中立 (Neutral)",
    2: "😍 好评 (Positive)",
    3: "⚪ 未提及 (None)"  
}

class SentimentPredictor:
    def __init__(self):
        print("⏳ 正在加载模型，请稍候...")
        self.device = Config.DEVICE
        self.tokenizer = BertTokenizer.from_pretrained(Config.BERT_PATH)
        
        # 1. 初始化模型结构
        self.model = MultiHeadBERT(Config)
        
        # 2. 加载训练好的权重
        model_path = f"{Config.MODEL_SAVE_DIR}/best_model.bin"
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        # 3. 开启评估模式 (非常重要！关闭 Dropout)
        self.model.to(self.device)
        self.model.eval()
        print("✅ 模型加载完成！")

    def predict(self, text):
        # 数据预处理 (和训练时一模一样)
        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=Config.MAX_LEN,
            padding='max_length',
            truncation=True,
            return_token_type_ids=False
        )
        
        ids = torch.tensor(inputs['input_ids'], dtype=torch.long).unsqueeze(0).to(self.device)
        mask = torch.tensor(inputs['attention_mask'], dtype=torch.long).unsqueeze(0).to(self.device)
        
        # 推理
        with torch.no_grad():
            # outputs 是一个包含 8 个 Tensor 的列表
            outputs = self.model(ids, mask)
        
        # 解析结果
        results = {}
        for i, logits in enumerate(outputs):
            dim_name = Config.TARGET_COLS[i]
            
            # logits 形状是 [1, 3]，我们需要找到概率最大的那个索引
            probs = torch.softmax(logits, dim=1) # 转换成概率
            pred_label_id = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred_label_id].item() # 置信度
            
            # 过滤逻辑：如果模型对结果很不自信（比如最大概率只有0.4），也可以视为未提及
            # 这里简单处理：直接输出预测结果
            results[dim_name] = {
                "label": ID2LABEL[pred_label_id],
                "score": f"{confidence:.2f}"
            }
            
        return results

if __name__ == "__main__":
    predictor = SentimentPredictor()
    
    # 测试用例
    test_sentences = [
        # 1. 【价格专项测试】检查刚才的补丁有没有生效（关键词：白嫖、两块钱、划算）
        "这也太划算了，一天才两块钱，四舍五入简直就是白嫖！以后就在你家租了。",

        # 2. 【画质专项测试】检查模型是否学会了“掉帧=差评”（关键词：PPT、优化差）
        "游戏优化极其垃圾，掌机模式下简直就是PPT，卡顿到无法呼吸，眼睛都要瞎了。",

        # 3. 【混合情感·难点】服务极好 + 游戏极差（测试模型是否会“情感串味”）
        "老板人超级好，半夜还回消息，发货也是秒发。但是这游戏真的太无聊了，剧情烂尾，狗都不玩。",

        # 4. 【混合情感·难点】游戏极好 + 成色极差（测试模型能否区分“内容”和“载体”）
        "异度之刃3的剧情和音乐真的是神级体验，哭得稀里哗啦。可惜发来的卡带金手指都黑了，擦了半天才读出来。",

        # 5. 【中立/一般评价测试】测试模型是否能识别“Neutral”（关键词：中规中矩、还行）
        "快递速度一般吧，三天到的，包装中规中矩，游戏玩起来也就那样，没网上吹得那么神。",

        # 6. 【多维度轰炸】测试模型能否同时捕捉 4-5 个维度
        "价格虽然有点小贵，但是顺丰特快真的稳。游戏画面是顶级的，就是配音有点出戏，听着难受。"
    ]
    
    print("\n" + "="*50)
    for text in test_sentences:
        print(f"\n📝 评论: {text}")
        analysis = predictor.predict(text)
        
        print("📊 分析结果:")
        for dim, res in analysis.items():
            print(f"   - {dim:<10}: {res['label']} (置信度: {res['score']})")
    print("\n" + "="*50)