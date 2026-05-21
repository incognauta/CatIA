"""
Servicio de Embeddings — Generación de vectores semánticos

Usa scikit-learn (TfidfVectorizer + TruncatedSVD) para producir vectores densos
de 384 dimensiones a partir de texto. Es un placeholder funcional que permite
búsqueda semántica real sin depender de redes neuronales pesadas.

Para producción, reemplazar con sentence-transformers/all-MiniLM-L6-v2:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text).tolist()
"""

import logging
import numpy as np
from functools import lru_cache
from typing import List, Optional

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSIONS = 384


class EmbeddingService:
    """
    Genera embeddings vectoriales para búsqueda semántica.

    Implementación actual: TF-IDF + SVD (384 dimensiones).
    Implementación futura: sentence-transformers (misma interfaz).
    """

    def __init__(self):
        self._pipeline = None
        self._fitted = False

    def _get_pipeline(self):
        if self._pipeline is None:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import TruncatedSVD
            from sklearn.pipeline import make_pipeline

            self._pipeline = make_pipeline(
                TfidfVectorizer(
                    max_features=10000,
                    stop_words='spanish',
                    lowercase=True,
                    analyzer='word',
                ),
                TruncatedSVD(n_components=EMBEDDING_DIMENSIONS, random_state=42),
            )
            logger.info("Embedding pipeline initialized (TF-IDF + SVD)")
        return self._pipeline

    def _fit_if_needed(self, texts: List[str]):
        if not self._fitted:
            pipeline = self._get_pipeline()
            pipeline.fit(texts)
            self._fitted = True
            logger.info(f"Embedding pipeline fitted on {len(texts)} texts")

    def encode(self, text: str) -> List[float]:
        """Generar embedding para un texto."""
        pipeline = self._get_pipeline()
        if self._fitted:
            vector = pipeline.transform([text])[0]
        else:
            vector = np.zeros(EMBEDDING_DIMENSIONS)
        return vector.tolist()

    def encode_batch(self, texts: List[str], fit: bool = True) -> List[List[float]]:
        """Generar embeddings para múltiples textos (entrena si es necesario)."""
        if not texts:
            return []
        if fit:
            self._fit_if_needed(texts)
        pipeline = self._get_pipeline()
        if self._fitted:
            vectors = pipeline.transform(texts)
        else:
            vectors = np.zeros((len(texts), EMBEDDING_DIMENSIONS))
        return [v.tolist() for v in vectors]


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Obtener instancia singleton del servicio de embeddings."""
    return EmbeddingService()
