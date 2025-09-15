from typing import Dict, Any, Optional, List
from pathlib import Path
from app.core.milvus import MilvusClient
from app.core.logger.logging_config_helper import get_configured_logger
from .document_loader import DocumentLoader
from .document_splitter import DocumentSplitter, ChunkConfig
from .document_embedder import DocumentEmbedder

logger = get_configured_logger("embedding_wrapper")

class DocumentProcessor:
    """文档处理器，整合加载、分块、向量化和存储功能"""
    
    def __init__(
        self,
        embedding_model: str = "text2vec-base",
        device: Optional[str] = None
    ):
        self.loader = DocumentLoader()
        self.embedder = DocumentEmbedder(model_name=embedding_model, device=device)
        self.milvus_client = MilvusClient()
    
    async def process(
        self,
        file_path: str,
        kb_type: str,  # 'department' or 'personal'
        owner_id: str,
        document_id: int,
        chunk_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理文档并存储到知识库"""
        try:
            # 1. 加载文档
            doc_data = await self.loader.load(file_path)
            
            # 2. 文档分块
            splitter = DocumentSplitter(ChunkConfig(**chunk_config))
            chunks = await splitter.split(doc_data["content"])
            
            # 3. 向量化
            chunks_with_vectors = await self.embedder.embed(chunks)
            
            # 4. 准备向量数据和元数据
            collection_name = f"{kb_type}_kb"
            vectors = []
            metadata = []
            
            for i, chunk in enumerate(chunks_with_vectors):
                vectors.append(chunk["vector"])
                metadata.append({
                    "chunk_id": i,  # 使用循环索引作为chunk_id
                    "document_id": document_id,
                    "text": chunk["content"],
                    **doc_data["metadata"],  # 添加原始文档元数据
                    "kb_type": kb_type,
                    "owner_id": owner_id
                })
            
            # 5. 确保collection存在并创建索引
            self.milvus_client.create_collection(
                collection_name=collection_name,
                dim=self.embedder.get_dimension()
            )
            self.milvus_client.create_index(collection_name)
            
            # 6. 插入数据
            self.milvus_client.insert(
                collection_name=collection_name,
                vectors=vectors,
                metadata=metadata
            )
            
            return {
                "status": "success",
                "file_name": Path(file_path).name,
                "kb_type": kb_type,
                "owner_id": owner_id,
                "document_id": document_id,
                "chunk_count": len(chunks),
                "vector_dimension": self.embedder.get_dimension()
            }
            
        except Exception as e:
            logger.error(f"处理文档失败: {e}", exc_info=True)
            raise
    
    async def search(
        self,
        kb_type: str,
        owner_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """搜索知识库"""
        try:
            # 1. 将查询文本向量化
            query_vector = self.embedder.model.encode(query).tolist()
            
            # 2. 构建过滤条件
            collection_name = f"{kb_type}_kb"
            filter_expr = f'owner_id == "{owner_id}"'
            
            # 3. 执行向量搜索
            results = self.milvus_client.search(
                collection_name=collection_name,
                vector=query_vector,
                top_k=top_k,
                filter_expr=filter_expr
            )
            
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}", exc_info=True)
            raise
    
    def delete_knowledge_base(self, kb_type: str):
        """删除知识库"""
        try:
            collection_name = f"{kb_type}_kb"
            self.milvus_client.delete_collection(collection_name)
        except Exception as e:
            logger.error(f"删除知识库失败: {e}", exc_info=True)
            raise
    
    def close(self):
        """关闭连接"""
        self.milvus_client.close()
    
    def __del__(self):
        """确保在对象销毁时关闭连接"""
        self.close()