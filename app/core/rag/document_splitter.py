from typing import List, Dict, Any
from dataclasses import dataclass

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    HTMLHeaderTextSplitter
)
from langchain.schema import Document
from app.core.logger.logging_config_helper import get_configured_logger
logger = get_configured_logger("embedding_wrapper")

@dataclass
class ChunkConfig:
    mode: str  # hierarchical, custom, auto
    max_size: int = 1000
    overlap_ratio: float = 0.1
    separators: List[str] = None

class DocumentSplitter:
    """基于LangChain的文档分块器"""
    
    def __init__(self, config: ChunkConfig):
        self.config = config
        self._validate_config()
    
    def _validate_config(self):
        """验证配置参数"""
        if self.config.mode not in ['hierarchical', 'custom', 'auto']:
            raise ValueError(f"不支持的分块模式: {self.config.mode}")
        if self.config.max_size <= 0:
            raise ValueError("分块大小必须大于0")
        if not 0 <= self.config.overlap_ratio < 1:
            raise ValueError("重叠比例必须在[0,1)范围内")
    
    async def split(self, content: str) -> List[Dict[str, Any]]:
        """根据配置的策略对文档进行分块"""
        try:
            if self.config.mode == 'hierarchical':
                chunks = await self._split_hierarchical(content)
            elif self.config.mode == 'custom':
                chunks = await self._split_custom(content)
            else:  # auto mode
                chunks = await self._split_auto(content)
            
            return [
                {
                    "content": chunk.page_content,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ]
        except Exception as e:
            logger.error(f"文档分块失败", exc_info=True)
            raise
    
    async def _split_hierarchical(self, content: str) -> List[Document]:
        """使用LangChain的MarkdownHeaderTextSplitter进行层级分块"""
        headers_to_split_on = [
            ("#", "header1"),
            ("##", "header2"),
            ("###", "header3"),
        ]
        
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        return splitter.split_text(content)
    
    async def _split_custom(self, content: str) -> List[Document]:
        """使用自定义分隔符的RecursiveCharacterTextSplitter"""
        if not self.config.separators:
            raise ValueError("自定义分块模式需要指定分隔符")
        
        chunk_size = self.config.max_size
        chunk_overlap = int(chunk_size * self.config.overlap_ratio)
        
        splitter = RecursiveCharacterTextSplitter(
            separators=self.config.separators,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        
        return splitter.create_documents([content])
    
    async def _split_auto(self, content: str) -> List[Document]:
        """使用自动分块的RecursiveCharacterTextSplitter"""
        chunk_size = self.config.max_size
        chunk_overlap = int(chunk_size * self.config.overlap_ratio)
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        
        return splitter.create_documents([content])