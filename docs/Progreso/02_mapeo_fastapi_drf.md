# Mapeo FastAPI -> Django REST Framework

Este documento explica que reemplaza que en la migracion.

## 1) Routing y endpoints

- FastAPI: `APIRouter` + decoradores `@router.get/post/...`
- DRF: `ViewSet` / `APIView` + `DefaultRouter` + `@action`

Equivalencia:

- `@router.post('/chat/message')` -> `@action(detail=False, methods=['post'])` en `ChatViewSet`
- `@router.get('/chat/history/{notebook}')` -> `@action(..., methods=['get'])` con query params o ruta custom

## 2) Validacion de entrada/salida

- FastAPI: `Pydantic BaseModel`
- DRF: `Serializer` / `ModelSerializer`

Equivalencia:

- `ChatRequest(BaseModel)` -> `ChatRequestSerializer(serializers.Serializer)`
- `DocumentResponse(BaseModel)` -> `DocumentSerializer(serializers.ModelSerializer)`

## 3) ORM y acceso a datos

- FastAPI (actual): SQLAlchemy
- DRF/Django: Django ORM

Equivalencia:

- `db.query(Document).filter(...).all()` -> `Document.objects.filter(...)`
- `db.add(obj); db.commit()` -> `obj.save()`

## 4) Auth y permisos

- FastAPI: JWT custom/manual
- DRF: `djangorestframework-simplejwt` + permisos DRF

Equivalencia:

- Endpoints de token custom -> `TokenObtainPairView` / `TokenRefreshView`
- Dependencias por endpoint -> `permission_classes` en vistas

## 5) Configuracion y CORS

- FastAPI: middlewares en app principal
- Django: settings + middleware chain

Equivalencia:

- `CORSMiddleware` -> `django-cors-headers`
- Settings sueltos -> `base.py`, `development.py`, `production.py`

## 6) Migraciones

- FastAPI/SQLAlchemy: Alembic
- Django: `makemigrations` + `migrate`

## 7) Admin

- FastAPI: no admin nativo
- Django: `django.contrib.admin` (panel listo para usar)

## 8) Documentacion API

- FastAPI: OpenAPI/Swagger nativo
- DRF: Swagger con `drf-yasg` o schema DRF

## Mapeo rapido de herramientas

| En FastAPI | En Django/DRF | Por que conviene aqui |
|---|---|---|
| APIRouter | Router + ViewSet | Convencion uniforme para CRUD + acciones |
| Pydantic | Serializer DRF | Validacion + serializacion integrada |
| SQLAlchemy | Django ORM | Menos friccion con admin/auth/migrations |
| JWT custom | simplejwt | Estandar y menos codigo manual |
| Alembic | Django migrations | Flujo integrado con modelos |
| Sin admin | Django admin | Gestion de usuarios/contenido inmediata |
