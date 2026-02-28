from typing import List, Dict, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


def smart_split(text: str, max_length: int = 500, overlap: int = 50, domain: str = "game") -> List[str]:
    """
    使用 LangChain 的 RecursiveCharacterTextSplitter 进行智能切分
    它会递归地尝试按段落、句子、单词等层级进行切分，尽可能保持语义完整性。
    
    Args:
        text: 要切分的文本
        max_length: 单个 chunk 的最大字符数
        overlap: chunk 之间的重叠字符数（保证上下文连贯性）
        domain: 领域类型 ('game', 'general')
    
    Returns:
        切分后的文本块列表
    """
    if not text or len(text.strip()) == 0:
        return []
    
    # 按领域设置分隔符（游戏评论有【标签】格式）
    separators = {
        "game": ["\n【", "\n\n", "\n", "。\n", "。", "！", "？", " ", ""],
        "general": ["\n\n", "\n", "。", "！", "？", " ", ""],
    }
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_length,
        chunk_overlap=overlap,
        separators=separators.get(domain, separators["general"]),
        add_start_index=True,  # 记录每个 chunk 在原文的位置
    )
    
    chunks = text_splitter.split_text(text)
    return chunks if chunks else []


def smart_split_with_metrics(
    text: str, 
    max_length: int = 500, 
    overlap: int = 50,
    domain: str = "game"
) -> Tuple[List[str], Dict]:
    """
    返回 (chunks, metrics)，便于监控和调试
    
    Returns:
        - chunks: 切分后的文本块
        - metrics: 切分质量指标
    """
    if not text or len(text.strip()) == 0:
        return [], {}
    
    separators = {
        "game": ["\n【", "\n\n", "\n", "。\n", "。", "！", "？", " ", ""],
        "general": ["\n\n", "\n", "。", "！", "？", " ", ""],
    }
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_length,
        chunk_overlap=overlap,
        separators=separators.get(domain, separators["general"]),
        add_start_index=True,
    )
    
    chunks = text_splitter.split_text(text)
    
    # 📊 质量指标
    metrics = {
        "total_chunks": len(chunks),
        "avg_chunk_size": sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
        "min_chunk_size": min((len(c) for c in chunks), default=0),
        "max_chunk_size": max((len(c) for c in chunks), default=0),
        "coverage_ratio": sum(len(c) for c in chunks) / len(text) if len(text) > 0 else 0,
    }
    
    logger.info(f"✅ Split metrics: {metrics}")
    
    return chunks, metrics


def load_and_split(file_path: str, max_length: int = 500, overlap: int = 50) -> Tuple[List[str], Dict]:
    """
    加载文档（支持多种格式）并切分
    
    支持格式: PDF, DOCX, TXT, MARKDOWN, HTML, EXCEL
    
    Args:
        file_path: 文件路径
        max_length: chunk 大小
        overlap: chunk 重叠
    
    Returns:
        - chunks: 切分后的文本
        - metadata: 文件元数据 + 切分指标
    """
    from document_loader import UniversalDocumentLoader
    from pathlib import Path
    
    # Step 1: 加载文档
    loader = UniversalDocumentLoader()
    texts, metadata = loader.load_document(file_path)
    
    # Step 2: 合并所有文本（因为某些格式可能分多部分）
    full_text = "\n\n".join(texts)
    
    # Step 3: 切分
    chunks, split_metrics = smart_split_with_metrics(full_text, max_length, overlap)
    
    # Step 4: 合并元数据
    combined_metadata = {
        **metadata,
        **split_metrics,
    }
    
    logger.info(f"📄 Successfully processed: {Path(file_path).name}")
    logger.info(f"   Chunks: {split_metrics['total_chunks']}, Avg size: {split_metrics['avg_chunk_size']:.0f}")
    
    return chunks, combined_metadata
