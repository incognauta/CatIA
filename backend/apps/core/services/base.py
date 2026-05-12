"""
Interfaces abstractas para servicios (DIP)

Define contratos que deben cumplir todas las implementaciones.
Permite intercambiar implementaciones sin afectar el resto del código.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class LLMServiceBase(ABC):
    """
    Interfaz abstracta para servicios de LLM (Large Language Model)
    
    Define el contrato que deben cumplir todos los proveedores de IA
    (Groq, OpenAI, local LLM, etc.)
    """
    
    @abstractmethod
    def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        context_documents: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        notebook_id: Optional[str] = None,
        model_override: Optional[str] = None,
        temperature_override: Optional[float] = None,
        max_tokens_override: Optional[int] = None,
    ) -> Dict:
        """
        Generar respuesta con contexto RAG
        
        Args:
            user_message: Mensaje del usuario
            system_prompt: Prompt del sistema (instrucciones)
            context_documents: Documentos para contexto RAG
            conversation_history: Historial previo
            notebook_id: ID del notebook (para logging)
            model_override: Sobrescribir modelo
            temperature_override: Sobrescribir temperatura
            max_tokens_override: Sobrescribir max tokens
        
        Returns:
            Dict con 'response' y 'tokens_used'
        """
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validar que la API key sea válida y funcional
        
        Returns:
            True si es válida, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Retornar lista de modelos disponibles
        
        Returns:
            Lista de dicts con {'value': 'model-id', 'label': 'Nombre modelo'}
        """
        pass


class DocumentServiceBase(ABC):
    """
    Interfaz abstracta para procesamiento de documentos
    
    Define el contrato para extraer y procesar contenido de archivos
    """
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extraer texto de un archivo
        
        Args:
            file_path: Ruta al archivo
        
        Returns:
            Texto extraído del documento
        """
        pass
    
    @abstractmethod
    def split_into_chunks(
        self,
        text: str,
        chunk_size: int,
        overlap: int = 0
    ) -> List[str]:
        """
        Dividir texto en chunks (fragmentos)
        
        Args:
            text: Texto a dividir
            chunk_size: Tamaño de cada chunk
            overlap: Caracteres de superposición entre chunks
        
        Returns:
            Lista de chunks
        """
        pass
    
    @abstractmethod
    def validate_file(self, file_obj) -> tuple[bool, str]:
        """
        Validar que el archivo sea procesable
        
        Args:
            file_obj: Objeto de archivo
        
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        pass


class RAGServiceBase(ABC):
    """
    Interfaz abstracta para servicios de RAG (Retrieval-Augmented Generation)
    """
    
    @abstractmethod
    def build_context(
        self,
        documents: List[Dict],
        query: str,
        max_chars: int = 3000
    ) -> str:
        """
        Construir contexto relevante a partir de documentos
        
        Args:
            documents: Lista de documentos {'title': ..., 'content': ...}
            query: Consulta del usuario
            max_chars: Máximo de caracteres en contexto
        
        Returns:
            String de contexto formateado
        """
        pass
    
    @abstractmethod
    def find_relevant_chunks(
        self,
        chunks: List[str],
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Encontrar chunks más relevantes para una query
        
        Args:
            chunks: Lista de chunks de texto
            query: Consulta del usuario
            top_k: Número de chunks más relevantes
        
        Returns:
            Chunks ordenados por relevancia
        """
        pass
