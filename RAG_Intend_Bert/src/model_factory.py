import os
from transformers import AutoModelForSequenceClassification, AutoConfig, AutoTokenizer

class ModelFactory:
    """
    模型工厂类：负责构建和加载模型及分词器。
    """
    @staticmethod
    def get_tokenizer(model_name: str):
        """
        获取分词器
        :param model_name: 预训练模型名称或路径
        :return: 分词器实例
        """
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        return tokenizer
    
    @staticmethod
    def get_model(model_path, num_labels, id2label=None, label2id=None):
        """
        统一的模型加载入口。
        无论是加载预训练模型(准备训练)，还是加载微调好的模型(准备推理)，都通过这个方法。
        :param model_path: 预训练模型名称或微调后模型路径
        :param num_labels: 分类标签数量
        :param id2label: 可选，ID 到标签的映射字典
        :param label2id: 可选，标签到 ID 的映射字典
        :return: 模型实例
        """
        return AutoModelForSequenceClassification.from_pretrained(
            model_path,
            num_labels=num_labels,
            id2label=id2label,
            label2id=label2id
        )
