"""
Servicios de la aplicación - DIP (Dependency Inversion Principle)

Este paquete contiene las interfaces abstractas y implementaciones
de servicios que encapsulan la lógica de negocio.
"""

from .base import LLMServiceBase, DocumentServiceBase
from .factory import LLMServiceFactory

__all__ = [
    'LLMServiceBase',
    'DocumentServiceBase',
    'LLMServiceFactory',
]
