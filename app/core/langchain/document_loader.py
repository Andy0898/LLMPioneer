from pathlib import Path
from typing import List
from langchain.schema import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    UnstructuredHTMLLoader,
)

from app.core.logger.logging_config_helper import get_configured_logger

logger = get_configured_logger(__name__)

class DocumentLoaderFactory:
    """
    Factory for creating and using LangChain document loaders.
    """
    _loaders = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".doc": Docx2txtLoader,
        ".md": UnstructuredMarkdownLoader,
        ".markdown": UnstructuredMarkdownLoader,
        ".txt": TextLoader,
        ".html": UnstructuredHTMLLoader,
        ".htm": UnstructuredHTMLLoader,
    }

    @classmethod
    def get_loader(cls, file_path: str):
        """
        Gets the appropriate document loader based on the file extension.

        Args:
            file_path: The path to the document.

        Returns:
            An instance of a LangChain document loader.
        """
        suffix = Path(file_path).suffix.lower()
        loader_class = cls._loaders.get(suffix)

        if not loader_class:
            logger.error(f"No loader available for file type: {suffix}")
            raise ValueError(f"Unsupported file type: {suffix}")

        return loader_class(file_path)

    @classmethod
    def load_documents(cls, file_path: str) -> List[Document]:
        """
        Loads a document from the given file path using the appropriate loader.

        Args:
            file_path: The path to the document.

        Returns:
            A list of LangChain Document objects.
        """
        logger.info(f"Loading document from: {file_path}")
        try:
            loader = cls.get_loader(file_path)
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} document(s).")
            return documents
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}", exc_info=True)
            raise
