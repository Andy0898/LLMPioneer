from typing import Dict, Any
from pathlib import Path
from app.config.logger import get_logger
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
    TextLoader
)
from langchain.schema import Document

logger = get_logger(__name__)

class DocumentLoader:
    """基于LangChain的文档加载器"""
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.doc': Docx2txtLoader,
            '.md': UnstructuredMarkdownLoader,
            '.markdown': UnstructuredMarkdownLoader,
            '.txt': TextLoader
        }
    
    async def load(self, file_path: str) -> Dict[str, Any]:
        """加载文档并返回文档内容和元数据"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        file_format = path.suffix.lower()
        if file_format not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {file_format}")
            
        try:
            # 使用LangChain的加载器
            loader_class = self.supported_formats[file_format]
            loader = loader_class(str(path))
            documents = loader.load()
            
            # 合并所有页面/文档的内容
            combined_content = "\n\n".join(doc.page_content for doc in documents)
            
            # 合并元数据
            combined_metadata = {}
            for doc in documents:
                combined_metadata.update(doc.metadata)
            
            combined_metadata.update({
                "file_name": path.name,
                "file_type": file_format,
                "file_size": path.stat().st_size
            })
            
            return {
                "content": combined_content,
                "metadata": combined_metadata
            }
            
        except Exception as e:
            logger.error(f"加载文档失败: {e}", exc_info=True)
            raise