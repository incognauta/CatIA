# 🚀 Valores de Environment para Render

Guía rápida de qué valores usar en Render para cada variable de entorno.

---

## Backend (catia-backend)

### Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30
```

### Environment Variables

| Variable | Valor | Notas |
|----------|-------|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | Usar settings de producción |
| `DEBUG` | `False` | ⚠️ Nunca `True` en producción |
| `SECRET_KEY` | `(Generar abajo)` | Copia generada con: `python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `DATABASE_URL` | `postgresql://...` | Copia de PostgreSQL creado en Render |
| `ALLOWED_HOSTS` | `catia-backend.onrender.com` | Dominio de Render (automático) |
| `CORS_ALLOWED_ORIGINS` | `https://catia-frontend.onrender.com` | URL del frontend en Render |
| `GROQ_API_KEY` | `gsk_...` | De https://console.groq.com/keys |
| `PYTHONUNBUFFERED` | `True` | Para ver logs en tiempo real |

---

## Frontend (catia-frontend)

### Build & Start Commands

**Build Command:**
```bash
npm install --legacy-peer-deps && npm run build
```

**Start Command:**
```bash
npm run preview
```

### Environment Variables

| Variable | Valor | Notas |
|----------|-------|-------|
| `VITE_API_BASE_URL` | `https://catia-backend.onrender.com/api/v1` | URL completa del backend |

---

## PostgreSQL (catia-db)

### Configuración Inicial

| Campo | Valor |
|-------|-------|
| **Name** | `catia-db` |
| **Database** | `catia` |
| **User** | `catia_user` |
| **Region** | `Frankfurt` (o tu región) |
| **PostgreSQL Version** | `15` |
| **Plan** | `Free` |

### Después de Creada

1. Verás "External Database URL" - **COPIAR COMPLETO**
2. Formato: `postgresql://catia_user:PASSWORD@hostname:5432/catia`
3. Pegar en Backend → `DATABASE_URL`

---

## Orden de Creación Recomendado

1. **PostgreSQL primero** → Obtener DATABASE_URL
2. **Backend** → Usar DATABASE_URL + GROQ_API_KEY
3. **Frontend** → Usar URL del Backend

---

## Urls Finales

| Servicio | URL |
|----------|-----|
| **Frontend** | `https://catia-frontend.onrender.com` |
| **Backend** | `https://catia-backend.onrender.com` |
| **API Base** | `https://catia-backend.onrender.com/api/v1` |
| **Admin Django** | `https://catia-backend.onrender.com/admin` |

---

## Health Checks

Después de desplegar:

```bash
# Backend
curl https://catia-backend.onrender.com/api/v1/health/
# Respuesta esperada: {"status": "ok"}

# Frontend
curl https://catia-frontend.onrender.com/
# Debe retornar HTML (aplicación React)
```

