"""
Servicios de la aplicación - DIP (Dependency Inversion Principle)

Este paquete contiene las interfaces abstractas y implementaciones
de servicios que encapsulan la lógica de negocio.

NOTA: Las implementaciones concretas se importan en las vistas para evitar
importes circulares. Las interfaces y factory se exportan aquí.
"""

from .base import (
    LLMServiceBase,
    DocumentServiceBase,
    RAGServiceBase,
    ChatServiceBase,
    DocumentUploadServiceBase,
    NotebookServiceBase,
)
from .factory import LLMServiceFactory
from .embedding_service import EmbeddingService, get_embedding_service

__all__ = [
    # Interfaces
    'LLMServiceBase',
    'DocumentServiceBase',
    'RAGServiceBase',
    'ChatServiceBase',
    'DocumentUploadServiceBase',
    'NotebookServiceBase',
    # Factory
    'LLMServiceFactory',
    # Embeddings
    'EmbeddingService',
    'get_embedding_service',
]
