from typing import List, Dict, Any
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from app.core.logger.logging_config_helper import get_configured_logger

logger = get_configured_logger(__name__)

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_SEPARATORS = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]

class DocumentSplitterFactory:
    """
    Factory for creating LangChain text splitters based on configuration.
    """

    @staticmethod
    def get_splitter(config: Dict[str, Any]):
        """
        Gets the appropriate text splitter based on the provided configuration.

        Args:
            config: A dictionary containing splitter configuration.
                    Expected keys: 'mode', 'max_size', 'overlap_ratio', 'separators'.

        Returns:
            An instance of a LangChain text splitter.
        """
        mode = config.get("mode", "recursive")
        max_size = config.get("max_size", DEFAULT_CHUNK_SIZE)
        overlap_ratio = config.get("overlap_ratio", 0.2) # Default to 0.2 if not provided
        chunk_overlap = int(max_size * overlap_ratio)

        logger.info(f"Creating splitter with mode: {mode}, chunk_size: {max_size}, chunk_overlap: {chunk_overlap}")

        if mode == "hierarchical":
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
            return MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        elif mode == "recursive":
            separators = config.get("separators") or DEFAULT_SEPARATORS
            return RecursiveCharacterTextSplitter(
                chunk_size=max_size,
                chunk_overlap=chunk_overlap,
                separators=separators,
                length_function=len,
            )
        
        else:
            logger.info(f"Unknown splitter mode: {mode}. Falling back to recursive splitter.")
            return RecursiveCharacterTextSplitter(
                chunk_size=max_size,
                chunk_overlap=chunk_overlap,
                separators=DEFAULT_SEPARATORS,
                length_function=len,
            )
