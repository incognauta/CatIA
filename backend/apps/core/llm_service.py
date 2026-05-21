"""
LLM Service: Groq API integration + RAG (Retrieval Augmented Generation)
Fase 7: Dependency Inversion Principle

Este módulo proporciona acceso a los servicios refactorizados usando el patrón DIP.
Mantiene compatibilidad hacia atrás importando desde services/.
"""
import logging
import re
from functools import lru_cache
from typing import List, Dict, Optional, Tuple

from django.conf import settings

# Importar desde services (DIP refactoring)
from .services.factory import LLMServiceFactory
from .services.base import LLMServiceBase

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)

# Configuración desde settings (Fase 6: Mejora)
GROQ_CONFIG = settings.GROQ_CONFIG
DOCUMENT_CONFIG = settings.DOCUMENT_CONFIG


class LLMServiceError(Exception):
    """Error en servicio LLM"""
    pass


# ═══════════════════════════════════════════════════════════
# Factory singleton para obtener instancia de servicio (Fase 7: DIP)
# ═══════════════════════════════════════════════════════════

@lru_cache(maxsize=1)
def get_llm_service() -> LLMServiceBase:
    """
    Obtener instancia singleton de LLMService
    
    Usa factory pattern para resolver la implementación.
    Thread-safe con functools.lru_cache.
    """
    return LLMServiceFactory.create_service('groq')


# ═══════════════════════════════════════════════════════════
# Utilidades de Chunking e Indexación (Fase 6: Mejora STEP 3)
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════

def split_into_chunks(
    text: str,
    chunk_size: int = None,
    overlap: int = None,
) -> List[str]:
    """
    Dividir texto en chunks con overlap para RAG.
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño del chunk (default: DOCUMENT_CONFIG)
        overlap: Caracteres de solapamiento entre chunks
    
    Returns:
        Lista de chunks
    """
    if chunk_size is None:
        chunk_size = DOCUMENT_CONFIG["CHUNK_SIZE"]
    if overlap is None:
        overlap = DOCUMENT_CONFIG["CHUNK_OVERLAP"]
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    step = chunk_size - overlap
    
    for i in range(0, len(text), step):
        chunk = text[i : i + chunk_size]
        if chunk.strip():  # Solo agregar si no está vacío
            chunks.append(chunk)
    
    return chunks


def find_relevant_chunks(
    chunks: List[str],
    query: str,
    top_k: int = 10,
) -> List[Tuple[str, float]]:
    """
    Encontrar chunks relevantes a la query usando búsqueda de keywords.
    
    Implementación simple sin embeddings (para evitar overhead).
    Usa: frecuencia de keywords, posición en documento, longitud.
    
    Args:
        chunks: Lista de chunks del documento
        query: Query del usuario
        top_k: Número de chunks a retornar
    
    Returns:
        Lista de tuplas (chunk, score) ordenadas por relevancia
    """
    # Normalizar query
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    
    if not query_words:
        # Si no hay keywords, retornar primeros chunks (inicio del documento)
        return [(chunk, 1.0) for chunk in chunks[:top_k]]
    
    scored_chunks = []
    
    for i, chunk in enumerate(chunks):
        chunk_words = set(re.findall(r'\b\w+\b', chunk.lower()))
        
        # Score basado en:
        # 1. Coincidencia de keywords
        matches = len(query_words & chunk_words)
        keyword_score = matches / len(query_words) if query_words else 0
        
        # 2. Posición (primeros chunks más relevantes)
        position_score = 1.0 - (i / max(len(chunks), 1)) * 0.3
        
        # 3. Longitud (chunks más largos = más info)
        length_score = min(len(chunk) / 1000, 1.0) * 0.2
        
        # Score combinado (ponderado)
        total_score = (keyword_score * 0.6) + (position_score * 0.2) + (length_score * 0.2)
        scored_chunks.append((chunk, total_score))
    
    # Ordenar por score y retornar top_k
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:top_k]


class LLMServiceError(Exception):
    """Error en servicio LLM"""
    pass


class GroqService:
    """
    Servicio centralizado para Groq API con RAG
    
    NOTA (Fase 7): Este es ahora un wrapper que delega al nuevo GroqLLMService
    del paquete services/. Se mantiene para compatibilidad hacia atrás.
    """
    
    def __init__(self):
        """Inicializar cliente Groq"""
        self._service = get_llm_service()
        self.model = GROQ_CONFIG.get('MODEL', 'llama-3.1-8b-instant')
        self.max_tokens = GROQ_CONFIG.get('MAX_TOKENS', 1024)
        self.temperature = GROQ_CONFIG.get('TEMPERATURE', 0.7)
    
    @staticmethod
    def build_rag_context(
        documents: List[Dict],
        query: Optional[str] = None,
        max_chars: Optional[int] = None,
    ) -> str:
        """
        Construir contexto RAG a partir de documentos relevantes.
        
        Implementación mejorada (Fase 6 STEP 3):
        - Chunking inteligente con overlap
        - Búsqueda semántica de fragmentos relevantes
        - Límites configurables por documento y total
        
        Args:
            documents: Lista de dicts con 'title' y 'content'
            query: Query del usuario (para búsqueda de relevancia)
            max_chars: Máximo de caracteres (default: DOCUMENT_CONFIG)
        
        Returns:
            String con contexto formateado
        """
        if not documents:
            return ""
        
        if max_chars is None:
            max_chars = DOCUMENT_CONFIG["MAX_CHARS_TOTAL"]
        
        max_per_doc = DOCUMENT_CONFIG["MAX_CHARS_PER_DOCUMENT"]
        enable_semantic = DOCUMENT_CONFIG["ENABLE_SEMANTIC_SEARCH"]
        
        context_parts = []
        total_chars = 0
        
        for doc in documents:
            title = doc.get('title', 'Documento sin título')
            content = doc.get('content', '')
            
            if not content:
                continue
            
            # Si el documento es muy largo y tenemos query, usar chunking inteligente
            if len(content) > max_per_doc and query and enable_semantic:
                # Dividir en chunks
                chunks = split_into_chunks(content)
                
                # Encontrar chunks relevantes
                relevant_chunks = find_relevant_chunks(chunks, query, top_k=2)
                selected_content = " ... ".join(chunk for chunk, _ in relevant_chunks)
                
                if len(selected_content) > max_per_doc:
                    selected_content = selected_content[:max_per_doc] + "..."
            else:
                # Simplemente truncar si es corto o semantic search deshabilitado
                selected_content = content[:max_per_doc]
            
            # Formatear parte del contexto
            part = f"📄 **{title}**\n{selected_content}\n"
            
            if total_chars + len(part) > max_chars:
                # Si no cabe, intentar agregar por lo menos algo truncado
                remaining = max_chars - total_chars
                if remaining > 100:
                    part = f"📄 **{title}**\n{selected_content[:remaining-20]}...\n"
                    context_parts.append(part)
                break
            
            context_parts.append(part)
            total_chars += len(part)
        
        result = "\n".join(context_parts)
        
        # Log para debugging
        if context_parts:
            logger.debug(
                f"RAG context built: docs={len(documents)}, "
                f"selected={len(context_parts)}, chars={total_chars}"
            )
        
        return result
    
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
        Generar respuesta con Groq + contexto RAG
        
        NOTA (Fase 7): Ahora delega al GroqLLMService.generate_response()
        pero mantiene la API compatible.
        
        Args:
            user_message: Mensaje del usuario
            system_prompt: Prompt del sistema (default: assistente educativo)
            context_documents: Documentos para RAG
            conversation_history: Historial de conversación previo
            notebook_id: ID del notebook (para logging)
            model_override: Sobrescribir modelo (Fase 6: para settings de usuario)
            temperature_override: Sobrescribir temperatura (Fase 6: para settings de usuario)
            max_tokens_override: Sobrescribir max_tokens (Fase 6: para settings de usuario)
        
        Returns:
            {
                'response': str,
                'tokens_used': int,
                'model': str,
                'stop_reason': str,
            }
        """
        try:
            # Sistema prompt por default
            if system_prompt is None:
                system_prompt = (
                    "Eres un asistente educativo especializado en procesar documentos. "
                    "Responde preguntas basadas en los documentos proporcionados. "
                    "Si la información no está en los documentos, indícalo claramente. "
                    "Mantén respuestas concisas y precisas."
                )
            
            # Delegar al servicio inyectado
            result = self._service.generate_response(
                user_message=user_message,
                system_prompt=system_prompt,
                context_documents=context_documents,
                conversation_history=conversation_history,
                notebook_id=notebook_id,
                model_override=model_override,
                temperature_override=temperature_override,
                max_tokens_override=max_tokens_override,
            )
            
            # Agregar stop_reason para compatibilidad
            if 'stop_reason' not in result:
                result['stop_reason'] = 'stop'
            
            return result
        
        except Exception as e:
            logger.error(f"Groq error: {str(e)}", exc_info=True)
            raise LLMServiceError(f"Error llamando a Groq: {str(e)}")
    
    @staticmethod
    def truncate_context(text: str, max_tokens: int = 4096) -> str:
        """
        Truncar texto a aproximadamente max_tokens
        (Groq usa ~4 caracteres por token en promedio)
        """
        chars_per_token = 4
        max_chars = max_tokens * chars_per_token
        
        if len(text) > max_chars:
            return text[:max_chars] + "... [truncado]"
        return text


# Singleton con thread-safety garantizado por @lru_cache
@lru_cache(maxsize=1)
def get_groq_service() -> GroqService:
    """
    Obtener instancia singleton de GroqService.
    
    Usa @lru_cache para garantizar:
    - Una única instancia en toda la aplicación
    - Thread-safe (no hay race conditions)
    - Cacheado automáticamente
    - Mejor que variables globales mutables
    
    Returns:
        GroqService: Instancia de servicio Groq
        
    Raises:
        LLMServiceError: Si Groq no está disponible
    """
    try:
        return GroqService()
    except LLMServiceError as e:
        logger.warning(f"Groq no disponible: {e}")
        raise
