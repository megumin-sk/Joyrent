import json
import joblib
import os
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

# ================= 配置 =================
# 这里我们需要把“垃圾评论”和“正常评论”合并成一个文件
# 假设你已经把上面生成的垃圾评论和原来的 train.json 合并成了 svm_train.json
DATA_PATH = r'D:\workspace\JoyRent\SwitchRent\comment-analysis\data\processed\svm_train.json'
MODEL_SAVE_PATH = r'D:\workspace\JoyRent\SwitchRent\comment-analysis\saved_models\svm_model\svm_spam_filter.pkl'

def train_svm():
    print("🚀 开始训练 SVM 垃圾评论分类器...")

    # 1. 加载数据
    if not os.path.exists(DATA_PATH):
        print(f"❌ 找不到数据文件: {DATA_PATH}")
        return

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = []
    labels = []

    print("   正在进行中文分词...")
    for item in data:
        # SVM 需要分词后的空格分隔字符串
        # 正常评论 label=1, 垃圾评论 label=0
        is_spam = item.get('is_spam', 0) 
        labels.append(item['label'])
        
        # 结巴分词: "塞尔达真好玩" -> "塞尔达 真 好玩"
        seg_list = jieba.cut(item['text'])
        texts.append(" ".join(seg_list))

    # 2. 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    # 3. 构建管道 (Pipeline)
    # 管道会自动执行：TF-IDF 向量化 -> SVM 分类
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000)), # 只保留最重要的5000个词
        ('clf', SVC(kernel='linear', probability=True))  # 线性核 SVM，速度最快
    ])

    # 4. 训练
    print("   正在训练 SVM...")
    pipeline.fit(X_train, y_train)

    # 5. 评估
    print("   评估模型:")
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=['Spam (垃圾)', 'Normal (正常)']))

    # 6. 保存模型
    joblib.dump(pipeline, MODEL_SAVE_PATH)
    print(f"💾 模型已保存至: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_svm()





    