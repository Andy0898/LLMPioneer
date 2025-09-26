from typing import List, Optional
from langchain.embeddings.base import Embeddings
from app.core.embedding import get_embedding, batch_get_embeddings
import asyncio

class CustomEmbeddings(Embeddings):
    """
    Custom LangChain Embeddings class that wraps our project's embedding functions.
    """
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None, timeout: int = 30):
        self.provider = provider
        self.model = model
        self.timeout = timeout

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.

        Args:
            texts: The list of texts to embed.

        Returns:
            A list of embeddings, one for each text.
        """
        try:
            # Use asyncio.run to execute the async batch_get_embeddings function
            return asyncio.run(batch_get_embeddings(
                texts=texts,
                provider=self.provider,
                model=self.model,
                timeout=self.timeout
            ))
        except Exception as e:
            # Handle cases where there's no running event loop or other errors
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(batch_get_embeddings(
                    texts=texts,
                    provider=self.provider,
                    model=self.model,
                    timeout=self.timeout
                ))
            finally:
                loop.close()
                asyncio.set_event_loop(None)


    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.

        Args:
            text: The text to embed.

        Returns:
            The embedding for the text.
        """
        try:
            # Use asyncio.run to execute the async get_embedding function
            return asyncio.run(get_embedding(
                text=text,
                provider=self.provider,
                model=self.model,
                timeout=self.timeout
            ))
        except Exception as e:
            # Handle cases where there's no running event loop or other errors
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(get_embedding(
                    text=text,
                    provider=self.provider,
                    model=self.model,
                    timeout=self.timeout
                ))
            finally:
                loop.close()
                asyncio.set_event_loop(None)

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Asynchronously embed a list of documents.

        Args:
            texts: The list of texts to embed.

        Returns:
            A list of embeddings, one for each text.
        """
        return await batch_get_embeddings(
            texts=texts,
            provider=self.provider,
            model=self.model,
            timeout=self.timeout
        )

    async def aembed_query(self, text: str) -> List[float]:
        """
        Asynchronously embed a single query.

        Args:
            text: The text to embed.

        Returns:
            The embedding for the text.
        """
        return await get_embedding(
            text=text,
            provider=self.provider,
            model=self.model,
            timeout=self.timeout
        )

