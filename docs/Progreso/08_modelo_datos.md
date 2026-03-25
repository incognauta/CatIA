# Modelo de Datos (Plan Inicial)

Fecha: 2026-03-18
Estado: Activo

## 1. Objetivo

Documentar entidades y relaciones para implementar Fase 2 sin ambiguedad.

## 2. Entidades principales

- User
- UserProfile
- Notebook
- Document
- ChatMessage
- Interaction

## 3. Relaciones esperadas

```text
User 1---1 UserProfile
User 1---N Notebook
User 1---N Document
User 1---N ChatMessage
User 1---N Interaction
Notebook 1---N Document
Notebook 1---N ChatMessage
Notebook 1---N Interaction
Document 1---N ChatMessage
Document 1---N Interaction
```

## 4. Campos clave (resumen)

### User

- id (UUID)
- email (unique)
- username
- role (FREE|PREMIUM|ADMIN)
- max_documents
- total_tokens_used

### UserProfile

- user (OneToOne)
- avatar
- bio
- preferencias UI

### Notebook

- id (UUID)
- user (FK)
- name
- slug
- color
- icon
- is_default

### Document

- id (UUID)
- user (FK)
- notebook (FK)
- original_filename
- file_path
- file_size
- pages
- content
- summary

### ChatMessage

- id (UUID)
- user (FK)
- notebook (FK o campo notebook segun implementacion)
- document (FK nullable)
- role (user|assistant)
- content
- tokens_used

### Interaction

- id (UUID)
- user (FK)
- notebook (FK nullable)
- document (FK nullable)
- interaction_type
- content
- ai_response
- metadata (JSON)
- context_snapshot (JSON)

## 5. Reglas de integridad

- Todo dato funcional debe estar asociado a `user`.
- No exponer datos de otro usuario en queries.
- `Document` y `ChatMessage` deben quedar ligados a notebook para contexto.
- `Interaction` registra eventos clave para memoria historica.

## 6. Indices recomendados

- User + notebook en tablas de alto volumen.
- created_at para orden y auditoria.
- campos de busqueda (`original_filename`, `slug`) cuando aplique.

## 7. Estrategia de migraciones

1. Crear modelo User custom primero.
2. Configurar `AUTH_USER_MODEL` antes de generar otras migraciones.
3. Crear UserProfile y Notebook.
4. Crear Document, ChatMessage, Interaction.
5. Ejecutar migraciones en orden y validar constraints.

## 8. Riesgos y mitigacion

- Riesgo: cambiar User tarde rompe migraciones.
  - Mitigacion: implementar User custom al inicio de Fase 2.
- Riesgo: sobrecarga de Interaction.
  - Mitigacion: indexar y paginar consultas historicas.
