"""
Servicio RAG Semántico — Búsqueda por similitud vectorial

Implementa RAGServiceBase usando embeddings almacenados en DocumentChunk.
Reemplaza el keyword matching por similitud coseno real entre vectores.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple

from django.conf import settings
from django.db import connection

from .base import RAGServiceBase
from .embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class SemanticRAGService(RAGServiceBase):
    """
    RAG Service con búsqueda semántica vectorial.

    Usa los embeddings almacenados en DocumentChunk para encontrar
    los fragmentos más relevantes por similitud coseno.
    """

    def build_context(
        self,
        documents: List[Dict],
        query: str,
        max_chars: int = 3000,
    ) -> str:
        """Construir contexto RAG usando búsqueda semántica."""
        if not documents or not query:
            return ""

        doc_ids = [d.get('id') for d in documents if d.get('id')]
        if not doc_ids:
            return self._fallback_keyword(documents, query, max_chars)

        # Generar embedding de la query
        emb = get_embedding_service()
        query_vector = emb.encode(query)

        # Buscar chunks más similares vía pgvector (cosine distance)
        similar_chunks = self._find_similar_chunks(query_vector, doc_ids, top_k=10)

        if not similar_chunks:
            return self._fallback_keyword(documents, query, max_chars)

        # Construir contexto formateado
        context = "## Contexto de documentos (búsqueda semántica):\n\n"
        total_chars = 0

        for chunk_text, title, score in similar_chunks:
            part = f"**{title}** (relevancia: {score:.2f}):\n{chunk_text}\n\n"
            if total_chars + len(part) <= max_chars:
                context += part
                total_chars += len(part)
            else:
                remaining = max_chars - total_chars
                if remaining > 100:
                    context += f"**{title}** (truncado):\n{chunk_text[:remaining]}...\n"
                break

        return context

    def _find_similar_chunks(
        self,
        query_vector: List[float],
        doc_ids: List[str],
        top_k: int = 10,
    ) -> List[Tuple[str, str, float]]:
        """
        Buscar chunks similares usando pgvector <=> (cosine distance).
        """
        vector_str = str(query_vector)
        placeholders = ', '.join(f"'{d}'" for d in doc_ids)

        sql = f"""
            SELECT
                dc.content,
                d.title,
                1 - (dc.embedding <=> '{vector_str}'::vector) AS similarity
            FROM documents_documentchunk dc
            JOIN documents_document d ON d.id = dc.document_id
            WHERE dc.document_id IN ({placeholders})
              AND dc.embedding IS NOT NULL
            ORDER BY dc.embedding <=> '{vector_str}'::vector
            LIMIT %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [top_k])
                rows = cursor.fetchall()
            return [(r[0], r[1], float(r[2])) for r in rows]
        except Exception as e:
            logger.warning(f"pgvector query failed, using fallback: {e}")
            return []

    def _fallback_keyword(
        self,
        documents: List[Dict],
        query: str,
        max_chars: int,
    ) -> str:
        """Fallback a keyword matching si no hay embeddings."""
        from .llm_service import GroqRAGService
        logger.info("Falling back to keyword RAG")
        return GroqRAGService().build_context(documents, query, max_chars)

    def find_relevant_chunks(
        self,
        chunks: List[str],
        query: str,
        top_k: int = 10,
    ) -> List[str]:
        """Encontrar chunks relevantes por similitud semántica."""
        if not chunks:
            return []

        emb = get_embedding_service()
        query_vector = np.array(emb.encode(query))
        chunk_vectors = np.array(emb.encode_batch(chunks, fit=False))

        # Similitud coseno
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        chunk_norms = chunk_vectors / (np.linalg.norm(chunk_vectors, axis=1, keepdims=True) + 1e-10)
        scores = np.dot(chunk_norms, query_norm)

        # Ordenar por score descendente
        indices = np.argsort(scores)[::-1][:top_k]
        return [chunks[i] for i in indices]

    @staticmethod
    def _split_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
        """Dividir texto en chunks con overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap if end < len(text) else end
        return chunks
