"""
Factory para crear instancias de servicios

Implementa el patrón Factory para resolver dependencias.
Permite cambiar implementaciones sin afectar el código cliente.
"""

import logging
from typing import Literal

from .base import LLMServiceBase
from .llm_service import GroqLLMService

logger = logging.getLogger(__name__)


class LLMServiceFactory:
    """
    Factory para crear instancias de LLMService
    
    Ejemplo:
        service = LLMServiceFactory.create_service('groq')
        response = service.generate_response("Hola")
    """
    
    # Registro de implementaciones disponibles
    _providers = {
        'groq': GroqLLMService,
        # Futuros proveedores:
        # 'openai': OpenAILLMService,
        # 'local': LocalLLMService,
    }
    
    @classmethod
    def create_service(
        cls,
        provider: Literal['groq'] = 'groq'
    ) -> LLMServiceBase:
        """
        Crear instancia de LLMService
        
        Args:
            provider: Proveedor a utilizar ('groq', 'openai', etc.)
        
        Returns:
            Instancia del servicio solicitado
        
        Raises:
            ValueError: Si el proveedor no está registrado
        """
        if provider not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Proveedor '{provider}' no registrado. "
                f"Disponibles: {available}"
            )
        
        service_class = cls._providers[provider]
        logger.info(f"Creating {provider} LLMService instance")
        
        return service_class()
    
    @classmethod
    def register_provider(cls, name: str, service_class):
        """
        Registrar un nuevo proveedor
        
        Args:
            name: Nombre del proveedor
            service_class: Clase que implementa LLMServiceBase
        """
        if not issubclass(service_class, LLMServiceBase):
            raise TypeError(
                f"{service_class} debe implementar LLMServiceBase"
            )
        
        cls._providers[name] = service_class
        logger.info(f"Registered provider: {name}")
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Retornar lista de proveedores registrados"""
        return list(cls._providers.keys())
