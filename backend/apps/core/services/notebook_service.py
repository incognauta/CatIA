"""
Implementación de NotebookService - Gestión de notebooks

Encapsula lógica de creación, recuperación y gestión de notebooks del usuario.
"""

import logging
from typing import Dict, List, Optional

from .base import NotebookServiceBase

logger = logging.getLogger(__name__)


class DjangoNotebookService(NotebookServiceBase):
    """
    Implementación de NotebookService usando Django models
    
    Orquesta:
    1. Obtención o creación de notebook default
    2. Listado de notebooks del usuario
    3. Operaciones CRUD básicas
    """
    
    def get_or_create_default(self, user_id: str) -> Dict:
        """
        Obtener o crear notebook default del usuario
        
        El notebook default es donde se clasifican documentos
        cuando el usuario no especifica un notebook explícitamente.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Dict con notebook {'id', 'name', 'slug', 'created_at', ...}
        
        Raises:
            ValueError: Si usuario no existe
        """
        from django.contrib.auth.models import User
        from apps.notebooks.models import Notebook
        from apps.notebooks.serializers import NotebookSerializer
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
        
        notebook, created = Notebook.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'Sin clasificar',
                'slug': 'sin-clasificar',
                'description': 'Notebook default para documentos sin clasificar',
            }
        )
        
        action = "creado" if created else "recuperado"
        logger.info(f"Notebook default {action}: {notebook.id}")
        
        serializer = NotebookSerializer(notebook)
        return serializer.data
    
    def get_user_notebooks(
        self,
        user_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Obtener todos los notebooks del usuario
        
        Retorna notebooks ordenados por fecha de creación (más recientes primero).
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de notebooks (None = todos)
        
        Returns:
            Lista de notebooks [{'id', 'name', 'slug', 'created_at', ...}, ...]
        
        Raises:
            ValueError: Si usuario no existe
        """
        from django.contrib.auth.models import User
        from apps.notebooks.models import Notebook
        from apps.notebooks.serializers import NotebookSerializer
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
        
        query = Notebook.objects.filter(user=user).order_by('-created_at')
        
        if limit:
            query = query[:limit]
        
        notebooks = list(query)
        
        logger.info(f"Recuperados {len(notebooks)} notebooks del usuario {user_id}")
        
        serializer = NotebookSerializer(notebooks, many=True)
        return serializer.data
