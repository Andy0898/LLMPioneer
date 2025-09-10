from typing import List, Dict, Any

import torch
from app.config.logger import get_logger
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

logger = get_logger(__name__)

class DocumentEmbedder:
    """基于LangChain的文档向量化器"""
    
    def __init__(self, model_name: str = "text2vec-base", device: str = None):
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': device if device else 'cuda' if torch.cuda.is_available() else 'cpu'}
            )
            logger.info(f"加载向量化模型成功: {model_name}")
        except Exception as e:
            logger.error(f"加载向量化模型失败: {e}", exc_info=True)
            raise
    
    async def embed(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将文本块转换为向量"""
        try:
            # 转换为LangChain文档格式
            documents = [
                Document(
                    page_content=chunk["content"],
                    metadata=chunk["metadata"]
                )
                for chunk in chunks
            ]
            
            # 批量生成向量
            embeddings = self.embeddings.embed_documents(
                [doc.page_content for doc in documents]
            )
            
            # 将向量添加到原始数据中
            for chunk, embedding in zip(chunks, embeddings):
                chunk["vector"] = embedding
                chunk["metadata"]["vector_dimension"] = len(embedding)
            
            return chunks
        except Exception as e:
            logger.error(f"文本向量化失败: {e}", exc_info=True)
            raise
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        # 通过生成一个示例向量来获取维度
        sample_embedding = self.embeddings.embed_query("测试文本")
        return len(sample_embedding)