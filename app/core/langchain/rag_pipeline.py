from typing import List, Dict, Any, Optional, Callable
import json
from langchain.schema import Document
from app.core.langchain.document_loader import DocumentLoaderFactory
from app.core.langchain.document_splitter import DocumentSplitterFactory
from app.core.langchain.embedding_provider import CustomEmbeddings
from app.core.retriever import get_vector_db_client
from app.core.logger.logging_config_helper import get_configured_logger

logger = get_configured_logger(__name__)

class RAGPipeline:
    """
    A pipeline for processing documents for Retrieval-Augmented Generation (RAG).
    This pipeline handles loading, splitting, embedding, and storing documents.
    """

    def __init__(self, splitter_config: Dict[str, Any], embedding_provider: Optional[str] = None, embedding_model: Optional[str] = None):
        """
        Initializes the RAG pipeline.

        Args:
            splitter_config: Configuration for the document splitter.
            embedding_provider: The name of the embedding provider to use.
            embedding_model: The name of the embedding model to use.
        """
        self.splitter_config = splitter_config
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.embeddings = CustomEmbeddings(provider=embedding_provider, model=embedding_model)
        self.vector_db_client = get_vector_db_client()

    async def process_and_store_file(
        self, 
        file_path: str, 
        document_info: Dict[str, Any],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, Any]:
        """
        Processes a single file through the entire pipeline and stores it in the vector DB.

        Args:
            file_path: The path to the file to process.
            document_info: A dictionary with details about the document (id, name, category_id, user_id).
            progress_callback: An async function to call with progress updates (status, percentage).

        Returns:
            A dictionary containing the status and the number of stored chunks.
        """
        logger.info(f"Starting RAG pipeline for file: {file_path}")

        # 1. Load Document
        if progress_callback: await progress_callback("loading", 0.1)
        try:
            documents = DocumentLoaderFactory.load_documents(file_path)
            if not documents:
                logger.warning(f"No documents were loaded from {file_path}.")
                return {"status": "failed", "message": "No content loaded from document."}
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise

        # 2. Split Document
        if progress_callback: await progress_callback("splitting", 0.3)
        try:
            splitter = DocumentSplitterFactory.get_splitter(self.splitter_config)
            chunks = splitter.split_documents(documents)
            logger.info(f"Split document into {len(chunks)} chunks.")
        except Exception as e:
            logger.error(f"Failed to split document: {e}")
            raise

        # 3. Embed Chunks
        if progress_callback: await progress_callback("embedding", 0.6)
        try:
            chunk_texts = [chunk.page_content for chunk in chunks]
            chunk_embeddings = await self.embeddings.aembed_documents(chunk_texts)
            logger.info(f"Successfully created embeddings for {len(chunk_embeddings)} chunks.")
        except Exception as e:
            logger.error(f"Failed to embed document chunks: {e}")
            raise

        if len(chunks) != len(chunk_embeddings):
            logger.error("Mismatch between number of chunks and number of embeddings.")
            raise ValueError("The number of chunks and embeddings must be the same.")

        # 4. Format for storage
        docs_to_upload = []
        for i, chunk in enumerate(chunks):
            doc_to_upload = {
                "id": f"{document_info['id']}_{i}",
                "url": file_path,
                "name": document_info.get('name', ''),
                "site": f"category_{document_info['category_id']}" if document_info.get('category_id') else f"user_{document_info['user_id']}",
                "schema_json": json.dumps({
                    "content": chunk.page_content,
                    "metadata": chunk.metadata,
                }),
                "embedding": chunk_embeddings[i],
            }
            docs_to_upload.append(doc_to_upload)

        # 5. Store in Vector DB
        if progress_callback: await progress_callback("storing", 0.9)
        try:
            await self.vector_db_client.upload_documents(docs_to_upload)
            logger.info(f"Successfully stored {len(docs_to_upload)} chunks in vector database.")
        except Exception as e:
            logger.error(f"Failed to store chunks in vector database: {e}")
            raise

        if progress_callback: await progress_callback("completed", 1.0)
        logger.info(f"Successfully processed and stored file {file_path}.")
        return {"status": "success", "chunks_stored": len(docs_to_upload)}
