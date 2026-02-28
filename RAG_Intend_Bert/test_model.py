import os
import json
import torch
import random
import sys
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report, accuracy_score

# Configuration
# Path to the trained model directory
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "bert_intent_classifier")
# Path to the raw dataset
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "row", "intends.json")

def predict(text, model, tokenizer, device, id2label):
    """
    Predict the intent of a single text input.
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_class_id = logits.argmax().item()
    return id2label[predicted_class_id], logits

def evaluate(model, tokenizer, device, data, id2label, label2id):
    """
    Evaluate the model on the provided dataset.
    """
    print(f"\n📊 Running evaluation on {len(data)} samples...")
    predictions = []
    true_labels = []
    
    # Progress bar effect
    total = len(data)
    for i, item in enumerate(data):
        text = item['text']
        true_label = item['label']
        
        # Checking if label exists in our model configuration
        if true_label not in label2id:
            print(f"Warning: Dataset label '{true_label}' not found in model config. Skipping.")
            continue

        pred_label, _ = predict(text, model, tokenizer, device, id2label)
        
        predictions.append(pred_label)
        true_labels.append(true_label)
        
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total} samples...")
            
    print("\n✅ Evaluation Results:")
    print(f"Accuracy: {accuracy_score(true_labels, predictions):.4f}")
    print("\nClassification Report:")
    print(classification_report(true_labels, predictions))

def main():
    # 1. Load Model & Tokenizer
    print(f"🏭 Loading model from: {MODEL_PATH}")
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"   Using device: {device}")
        
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH).to(device)
        
        # Get labels from model config
        id2label = model.config.id2label
        label2id = model.config.label2id
        print(f"   Model labels: {label2id}")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("Please ensure the model path is correct and the model is trained/saved.")
        sys.exit(1)
    
    # 2. Load Data
    print(f"\n📂 Loading dataset from: {DATA_PATH}")
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Dataset file not found at {DATA_PATH}")
        sys.exit(1)
        
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 3. Run Evaluation
    # Evaluate on a random sample to save time if dataset is huge, or full dataset
    # Here we evaluate full dataset as it is fast for BERT on ~1500 samples
    evaluate(model, tokenizer, device, data, id2label, label2id)
    
    # 4. Interactive Test
    print("\n---------------------------------------------------")
    print("🎮 Interactive Test Mode")
    print("Type a game-related question to test functionality.")
    print("Type 'exit' or 'quit' to stop.")
    print("---------------------------------------------------")
    
    while True:
        try:
            text = input("\nYour Input > ")
            if text.lower() in ['exit', 'quit']:
                print("Goodbye! 👋")
                break
            if not text.strip():
                continue
                
            label, logits = predict(text, model, tokenizer, device, id2label)
            scores = torch.softmax(logits, dim=1).cpu().numpy()[0]
            
            print(f"➜ Predicted Intent: {label}")
            print("➜ Confidence Scores:")
            for i, score in enumerate(scores):
                label_name = id2label[i]
                bar_len = int(score * 20)
                bar = '█' * bar_len + '░' * (20 - bar_len)
                print(f"   {label_name.ljust(6)}: {bar} {score:.4f}")
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
