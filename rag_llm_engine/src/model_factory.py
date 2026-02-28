import os
from langchain_community.chat_models import ChatTongyi
from config import Config

import logging

class ModelFactory:
    @staticmethod
    def get_llm(model_name=Config.LLM_MODEL, temperature=0.0):
        """
        创建并返回一个新的 ChatTongyi 实例。
        这个方法类似于 Java 中的静态工厂方法。
        """
        api_key = Config.DASHSCOPE_API_KEY
        if not api_key:
            raise ValueError("未在 Config 中找到 DASHSCOPE_API_KEY")

        try:
            # 每次调用直接创建一个新对象
            llm = ChatTongyi(
                model=model_name,
                temperature=float(temperature),
                dashscope_api_key=api_key
            )
            return llm
        except Exception as e:
            logging.error(f"创建 ChatTongyi 实例失败: {e}")
            raise e
