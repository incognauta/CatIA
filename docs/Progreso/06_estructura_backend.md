# Estructura Backend

Fecha: 2026-03-18
Estado: Activo

## 1. Estructura actual

```text
backend/
  manage.py
  requirements.txt
  .env
  .env.example
  Dockerfile
  config/
    urls.py
    asgi.py
    wsgi.py
    settings/
      base.py
      development.py
      production.py
  apps/
    users/
    notebooks/
    interactions/
    documents/
    chat/
    core/
```

## 2. Responsabilidad por carpeta

- `config/`: configuracion global Django.
- `config/settings/`: configuracion por entorno.
- `apps/`: dominios funcionales.
- `apps/core/`: utilidades transversales (errores, helpers comunes).

## 3. Patron recomendado por app

Cada app debe mantener esta forma minima:

```text
apps/<app_name>/
  __init__.py
  apps.py
  models.py
  serializers.py
  views.py
  urls.py
  admin.py
  tests.py
  services.py        # si aplica logica de negocio
  permissions.py     # si aplica permisos custom
```

## 4. Reglas de organizacion

- No mezclar logica de negocio compleja en `views.py`.
- Usar `services.py` para procesos (ej: parse PDF, llamada Groq).
- Mantener serializacion/validacion en `serializers.py`.
- Mantener permisos en `permissions.py`.

## 5. Configuracion por entorno

- `base.py`: defaults comunes.
- `development.py`: debug y permisos relajados de desarrollo.
- `production.py`: seguridad estricta.

## 6. Paso a paso para agregar una nueva app

1. Crear app en `apps/`.
2. Corregir `apps.py` con nombre completo (`apps.<nombre>`).
3. Registrar app en `INSTALLED_APPS`.
4. Crear `urls.py` de app.
5. Incluir rutas en `config/urls.py`.
6. Crear modelos y migraciones.
7. Escribir tests basicos.
8. Actualizar docs tracker.

## 7. Criterio de calidad minimo por PR

- `python manage.py check` sin errores.
- migraciones aplicables.
- endpoint probado manualmente.
- documentacion actualizada.
