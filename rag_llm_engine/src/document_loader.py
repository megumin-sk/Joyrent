"""
多格式文档加载器
支持: PDF, WORD, EXCEL, MARKDOWN, HTML, TXT
"""

import os
from typing import List, Tuple, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class UniversalDocumentLoader:
    """通用文档加载器"""
    
    @staticmethod
    def load_pdf(file_path: str) -> List[str]:
        """加载 PDF 文件"""
        try:
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            # 每页为一个文档
            texts = [doc.page_content for doc in docs]
            logger.info(f"✅ Loaded PDF: {len(texts)} pages")
            return texts
        except ImportError:
            logger.error("❌ PyPDFLoader not installed. Run: pip install pypdf")
            raise

    @staticmethod
    def load_docx(file_path: str) -> List[str]:
        """加载 Word (.docx) 文件"""
        try:
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
            texts = [doc.page_content for doc in docs]
            logger.info(f"✅ Loaded DOCX: {len(texts)} documents")
            return texts
        except ImportError:
            logger.error("❌ Docx2txtLoader not installed. Run: pip install python-docx")
            raise

    @staticmethod
    def load_markdown(file_path: str) -> List[str]:
        """加载 Markdown 文件"""
        try:
            from langchain_community.document_loaders import UnstructuredMarkdownLoader
            loader = UnstructuredMarkdownLoader(file_path)
            docs = loader.load()
            texts = [doc.page_content for doc in docs]
            logger.info(f"✅ Loaded Markdown: {len(texts)} documents")
            return texts
        except ImportError:
            # 降级方案：直接读取
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.warning("⚠️ Using fallback markdown loader")
            return [text]

    @staticmethod
    def load_txt(file_path: str) -> List[str]:
        """加载纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"✅ Loaded TXT: {len(text)} chars")
            return [text]
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                text = f.read()
            logger.warning("⚠️ Loaded TXT with GBK encoding")
            return [text]

    @staticmethod
    def load_excel(file_path: str) -> List[str]:
        """加载 Excel 文件"""
        try:
            from langchain_community.document_loaders import UnstructuredExcelLoader
            loader = UnstructuredExcelLoader(file_path)
            docs = loader.load()
            texts = [doc.page_content for doc in docs]
            logger.info(f"✅ Loaded Excel: {len(texts)} sheets")
            return texts
        except ImportError:
            # 降级方案：用 pandas
            import pandas as pd
            xls = pd.ExcelFile(file_path)
            texts = []
            for sheet in xls.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet)
                text = df.to_string()
                texts.append(text)
            logger.warning("⚠️ Using pandas as fallback for Excel")
            return texts

    @staticmethod
    def load_html(file_path: str) -> List[str]:
        """加载 HTML 文件"""
        try:
            from langchain_community.document_loaders import UnstructuredHTMLLoader
            loader = UnstructuredHTMLLoader(file_path)
            docs = loader.load()
            texts = [doc.page_content for doc in docs]
            logger.info(f"✅ Loaded HTML: {len(texts)} documents")
            return texts
        except ImportError:
            # 降级方案：用 BeautifulSoup
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                text = soup.get_text()
            logger.warning("⚠️ Using BeautifulSoup as fallback for HTML")
            return [text]

    @classmethod
    def load_document(cls, file_path: str) -> Tuple[List[str], Dict]:
        """
        智能加载文档（根据文件扩展名）
        返回 (texts, metadata)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"❌ File not found: {file_path}")
        
        # 元数据
        metadata = {
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_type": file_path.suffix.lower(),
        }
        
        # 根据扩展名加载
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            texts = cls.load_pdf(str(file_path))
        elif suffix == '.docx':
            texts = cls.load_docx(str(file_path))
        elif suffix == '.md':
            texts = cls.load_markdown(str(file_path))
        elif suffix == '.xlsx' or suffix == '.xls':
            texts = cls.load_excel(str(file_path))
        elif suffix == '.html' or suffix == '.htm':
            texts = cls.load_html(str(file_path))
        elif suffix == '.txt':
            texts = cls.load_txt(str(file_path))
        else:
            raise ValueError(f"❌ Unsupported file format: {suffix}")
        
        metadata["total_texts"] = len(texts)
        metadata["total_chars"] = sum(len(t) for t in texts)
        
        logger.info(f"📄 Loaded document: {metadata}")
        
        return texts, metadata


# 使用示例
if __name__ == "__main__":
    # 测试
    loader = UniversalDocumentLoader()
    
    # 例1：加载 PDF
    # texts, meta = loader.load_document("sample.pdf")
    
    # 例2：加载 Word
    # texts, meta = loader.load_document("sample.docx")
    
    # 例3：加载 TXT
    texts, meta = loader.load_document("sample.txt")
    print(meta)
