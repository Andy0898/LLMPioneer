from typing import List, Dict, Any, Optional
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from app.config import settings
import signal
import sys
from app.config.logger import get_logger

logger = get_logger(__name__)

class MilvusClient:
    def __init__(self):
        """初始化Milvus客户端"""
        self._connect()
        # 注册信号处理器以确保在进程终止时关闭连接
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _connect(self):
        """连接到Milvus服务器"""
        try:
            logger.info(f"连接到Milvus服务器: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
            connections.connect(
                alias="default",
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
                user=settings.MILVUS_USER,
                password=settings.MILVUS_PASSWORD
            )
        except Exception as e:
            logger.error(f"连接到Milvus服务器失败: {e}", exc_info=True)
            sys.exit(1)  # 退出程序

    def create_collection(self, collection_name: str, dim: int = 1536) -> Collection:
        """创建向量集合"""
        try:
            if utility.exists_collection(collection_name):
                return Collection(collection_name)

            # 定义字段
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="chunk_id", dtype=DataType.INT64),
                FieldSchema(name="document_id", dtype=DataType.INT64),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim)
            ]

            # 创建集合schema
            schema = CollectionSchema(
                fields=fields,
                description=f"Document chunks collection for {collection_name}"
            )

            # 创建集合
            collection = Collection(
                name=collection_name,
                schema=schema,
                using='default',
                shards_num=2
            )

            return collection
        except Exception as e:
            logger.error(f"创建集合失败: {e}", exc_info=True)
            return None

    def insert(self, collection_name: str, vectors: List[List[float]], metadata: List[Dict[str, Any]]):
        """插入向量数据"""
        try:
            # 确保集合存在
            collection = self.create_collection(collection_name)
            if collection is None:
                return

            # 准备插入数据
            data = [
                [m['chunk_id'] for m in metadata],  # chunk_ids
                [m['document_id'] for m in metadata],  # document_ids
                [m['text'] for m in metadata],  # texts
                vectors  # vectors
            ]
            
            # 插入数据
            collection.insert(data)
            
            # 加载集合到内存
            collection.load()
        except Exception as e:
            logger.error(f"插入数据失败: {e}", exc_info=True)

    def create_index(self, collection_name: str, index_type: str = "IVF_FLAT", metric_type: str = "L2"):
        """创建索引"""
        try:
            collection = Collection(collection_name)
            
            # 创建索引
            index_params = {
                "metric_type": metric_type,
                "index_type": index_type,
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="vector", index_params=index_params)
            
            # 加载集合到内存
            collection.load()
        except Exception as e:
            logger.error(f"创建索引失败: {e}", exc_info=True)

    def search(
        self,
        collection_name: str,
        vector: List[float],
        top_k: int = 5,
        filter_expr: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索相似向量"""
        try:
            collection = Collection(collection_name)
            collection.load()

            # 执行搜索
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = collection.search(
                data=[vector],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=["chunk_id", "document_id", "text"]
            )

            # 格式化结果
            hits = []
            for hits_i, distances_i in zip(results[0], results[0].distances):
                hit = {
                    "chunk_id": hits_i.entity.get('chunk_id'),
                    "document_id": hits_i.entity.get('document_id'),
                    "text": hits_i.entity.get('text'),
                    "distance": distances_i
                }
                hits.append(hit)

            return hits
        except Exception as e:
            logger.error(f"搜索失败: {e}", exc_info=True)
            return []

    def delete_collection(self, collection_name: str):
        """删除集合"""
        try:
            if utility.exists_collection(collection_name):
                utility.drop_collection(collection_name)
        except Exception as e:
            logger.error(f"删除集合失败: {e}", exc_info=True)

    def close(self):
        """关闭连接"""
        logger.info("关闭连接...")
        connections.disconnect("default")

    def _signal_handler(self, signum, frame):
        """信号处理器，确保在接收到终止信号时关闭连接"""
        logger.info("接收到终止信号，正在关闭连接...")
        self.close()
        sys.exit(0)

    def __del__(self):
        """析构函数，确保关闭连接"""
        self.close()
    
    def get_document_chunks(
        self,
        collection_name: str,
        document_id: int
    ) -> List[Dict[str, Any]]:
        """获取指定文档的所有分块"""
        try:
            collection = Collection(collection_name)
            collection.load()

            # 构建查询条件
            expr = f'document_id == {document_id}'
            
            # 执行查询
            results = collection.query(
                expr=expr,
                output_fields=["chunk_id", "document_id", "text"]
            )

            # 格式化结果
            chunks = []
            for result in results:
                chunk = {
                    "chunk_id": result.get('chunk_id'),
                    "document_id": result.get('document_id'),
                    "text": result.get('text')
                }
                chunks.append(chunk)

            return chunks
        except Exception as e:
            logger.error(f"获取文档分块失败: {e}", exc_info=True)
            return []