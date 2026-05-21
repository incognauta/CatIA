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
        language: str = 'es',
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
            language: Idioma de la respuesta ('es' o 'en')
        
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


class ChatServiceBase(ABC):
    """
    Interfaz abstracta para lógica de negocio del chat
    
    Orquesta la interacción entre documentos, LLM y historial de conversación.
    Define el contrato para procesar preguntas del usuario con contexto RAG.
    """
    
    @abstractmethod
    def process_query(
        self,
        user_id: str,
        notebook_id: str,
        message: str,
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """
        Procesar pregunta del usuario con contexto RAG
        
        Args:
            user_id: ID del usuario
            notebook_id: ID del notebook
            message: Mensaje del usuario
            system_prompt: Prompt del sistema (instrucciones) opcional
        
        Returns:
            Dict con resultado completo del chat
        """
        pass
    
    @abstractmethod
    def get_conversation_history(
        self,
        user_id: str,
        notebook_id: str,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Obtener historial de conversación
        
        Args:
            user_id: ID del usuario
            notebook_id: ID del notebook
            limit: Número máximo de mensajes a retornar
        
        Returns:
            Lista de mensajes [{'role': 'user'/'assistant', 'content': ...}]
        """
        pass
    
    @abstractmethod
    def clear_history(
        self,
        user_id: str,
        notebook_id: str,
    ) -> int:
        """
        Limpiar historial de conversación
        
        Args:
            user_id: ID del usuario
            notebook_id: ID del notebook
        
        Returns:
            Número de mensajes eliminados
        """
        pass


class DocumentUploadServiceBase(ABC):
    """
    Interfaz abstracta para procesamiento de documentos (carga y procesamiento)
    
    Define el contrato para procesar archivos cargados por usuarios.
    """
    
    @abstractmethod
    def process_upload(
        self,
        uploaded_file,
        notebook_id: Optional[str],
        user_id: str,
        title: Optional[str] = None,
    ) -> Dict:
        """
        Procesar archivo cargado
        
        Args:
            uploaded_file: Archivo cargado desde request.FILES
            notebook_id: ID del notebook (usa default si es None)
            user_id: ID del usuario
            title: Título del documento (usa filename si no lo proporciona)
        
        Returns:
            Dict con documento procesado {'id', 'title', 'content', ...}
        """
        pass
    
    @abstractmethod
    def validate_file(self, uploaded_file) -> tuple[bool, str]:
        """
        Validar que el archivo sea soportado
        
        Args:
            uploaded_file: Archivo a validar
        
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        pass


class NotebookServiceBase(ABC):
    """
    Interfaz abstracta para lógica de negocio de notebooks
    
    Define el contrato para gestionar notebooks del usuario.
    """
    
    @abstractmethod
    def get_or_create_default(self, user_id: str) -> Dict:
        """
        Obtener o crear notebook default del usuario
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Dict con notebook {'id', 'name', 'slug', 'created_at', ...}
        """
        pass
    
    @abstractmethod
    def get_user_notebooks(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Obtener todos los notebooks del usuario
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de notebooks (None = todos)
        
        Returns:
            Lista de notebooks ordenados por fecha de creación
        """
        pass
