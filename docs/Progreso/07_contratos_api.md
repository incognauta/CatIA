# Contratos API (Base)

Fecha: 2026-03-18
Estado: Activo
Version API: v1

## 1. Convenciones generales

- Prefijo: `/api/v1/`.
- Formato: JSON.
- Auth: Bearer JWT para endpoints protegidos.
- Fechas: ISO-8601.
- IDs: UUID cuando aplique.

## 2. Estandar de respuesta

### 2.1 Respuesta exitosa

```json
{
  "data": {},
  "message": "optional",
  "meta": {}
}
```

### 2.2 Respuesta de error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input invalido",
    "details": {}
  }
}
```

## 3. Endpoints base ya activos

### 3.1 Health check

- Metodo: `GET`
- Ruta: `/health/`
- Auth: no
- Uso: verificar que el backend esta arriba.

Respuesta actual:

```json
{
  "status": "ok",
  "service": "pdf_ia_rework_backend"
}
```

## 4. Endpoints planificados (fase 2-4)

### 4.1 Auth

- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/token/refresh/`
- `GET /api/v1/auth/profile/`

### 4.2 Notebooks

- `GET /api/v1/notebooks/`
- `POST /api/v1/notebooks/`
- `PATCH /api/v1/notebooks/{id}/`
- `POST /api/v1/notebooks/{id}/archive/`

### 4.3 Documents

- `POST /api/v1/documents/upload/`
- `GET /api/v1/documents/`
- `GET /api/v1/documents/{id}/`
- `POST /api/v1/documents/{id}/generate_summary/`

### 4.4 Chat

- `POST /api/v1/chat/send_message/`
- `GET /api/v1/chat/history/?notebook=<id|slug>`
- `DELETE /api/v1/chat/clear_history/?notebook=<id|slug>`

## 5. Mapeo FastAPI -> DRF de trabajo

- APIRouter endpoint -> ViewSet action.
- Pydantic request model -> DRF Serializer.
- SQLAlchemy query -> Django ORM queryset.
- JWT custom endpoint -> simplejwt views.

## 6. Criterios de contrato estable

Antes de liberar un endpoint a frontend:

1. definir request schema;
2. definir response schema;
3. definir status codes esperados;
4. documentar errores comunes;
5. agregar test basico de endpoint.
