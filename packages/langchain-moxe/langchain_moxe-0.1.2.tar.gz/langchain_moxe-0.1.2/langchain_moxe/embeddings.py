from typing import List, Optional
from langchain_core.embeddings import Embeddings
from .client import MoxeClient


class MoxeEmbeddings(Embeddings):
    """Wrapper de embeddings da Moxe via /embedding/generate."""

    model: str = "text-embedding-001"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60

    def __init__(self, model: str = "text-embedding-001", api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 60):
        super().__init__()
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client = MoxeClient(api_key=api_key, base_url=base_url, timeout=timeout)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_single(text)

    def _embed_single(self, text: str) -> List[float]:
        resp = self._client.embedding_generate(text=text, model_name=self.model)
        # Ajuste aqui conforme o formato real retornado pelo /embedding/generate
        # Ex.: {"embedding": [..]} ou {"data": {"embedding": [..]}}
        if "embedding" in resp:
            return resp["embedding"]
        if "data" in resp and isinstance(resp["data"], dict) and "embedding" in resp["data"]:
            return resp["data"]["embedding"]
        # fallback
        raise ValueError(f"Resposta inesperada de embeddings: {resp}")
