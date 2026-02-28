import joblib
import jieba
import sys
import os

# 导入你的 BERT 推理类
from inference import SentimentPredictor

# 配置模型路径
SVM_MODEL_PATH = r'D:\workspace\JoyRent\SwitchRent\comment-analysis\saved_models\svm_model\svm_spam_filter.pkl'

class ContentSecuritySystem:
    def __init__(self):
        print("🛡️  正在初始化内容安全系统...")
        
        # 1. 加载 SVM (门卫)
        if not os.path.exists(SVM_MODEL_PATH):
            raise FileNotFoundError(f"找不到 SVM 模型: {SVM_MODEL_PATH}")
        print("   - 加载 SVM 垃圾拦截器...")
        self.svm = joblib.load(SVM_MODEL_PATH)
        
        # 2. 加载 BERT (专家)
        print("   - 加载 BERT 情感分析引擎...")
        self.bert = SentimentPredictor() # 这里面已经包含了加载逻辑
        
        print("✅ 系统初始化完毕！随时待命。\n")

    def process_comment(self, text):
        print(f"📨 收到新评论: 「{text}」")
        
        # --- 第一关：SVM 垃圾检测 ---
        # SVM 训练时用了分词，所以预测时也要分词
        seg_text = " ".join(jieba.cut(text))
        is_normal = self.svm.predict([seg_text])[0] # 0:垃圾, 1:正常
        
        # 获取置信度 (概率)
        probs = self.svm.predict_proba([seg_text])[0]
        spam_prob = probs[0]
        
        if is_normal == 0:
            print(f"🚫 [拦截] 被 SVM 判定为垃圾信息 (垃圾概率: {spam_prob:.2%})")
            return {
                "status": "block",
                "reason": "spam_detected"
            }
            
        print(f"✅ [通过] SVM 判定为正常内容 (正常概率: {probs[1]:.2%})")
        print("   -> 正在转交 BERT 进行深度分析...")
        
        # --- 第二关：BERT 情感分析 ---
        analysis_result = self.bert.predict(text)
        
        # 打印一下结果
        print("📊 [分析完成] BERT 报告:")
        for dim, res in analysis_result.items():
            if res['label'] != "⚪ 未提及 (None)":
                print(f"      - {dim}: {res['label']} ({res['score']})")
                
        return {
            "status": "success",
            "data": analysis_result
        }

if __name__ == "__main__":
    # 实例化系统
    security_system = ContentSecuritySystem()
    
    # 模拟真实数据流
    test_cases = [
        "诚信兼职，日入三百，加V：wx123456",            # 明显垃圾
        "asdfghjkl",                                   # 乱码
        "塞尔达真的是神作，但是快递太慢了，走了五天！",    # 正常差评
        "价格公道，成色很新，下次还来。",                 # 正常好评
        "加我V看刺激视频：http://t.cn/xx",              # 广告
        "画面掉帧严重，不过剧情确实感人。"                # 复杂评论
    ]
    
    print("="*60)
    for comment in test_cases:
        security_system.process_comment(comment)
        print("-"*60)