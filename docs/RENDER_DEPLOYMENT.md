# 🚀 Guía de Despliegue en Render con CI/CD

**Versión:** 1.0  
**Última actualización:** 26 de mayo de 2026  
**Plataforma:** Render.com  
**Ambiente:** Desarrollo/Testing  
**CI/CD:** Automático con GitHub

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Paso 1: Preparar GitHub](#paso-1-preparar-github)
3. [Paso 2: Crear Cuenta en Render](#paso-2-crear-cuenta-en-render)
4. [Paso 3: Crear PostgreSQL](#paso-3-crear-postgresql)
5. [Paso 4: Desplegar Backend](#paso-4-desplegar-backend)
6. [Paso 5: Desplegar Frontend](#paso-5-desplegar-frontend)
7. [Paso 6: Verificar Despliegue](#paso-6-verificar-despliegue)
8. [Monitoreo y Troubleshooting](#monitoreo-y-troubleshooting)

---

## ✅ Requisitos Previos

- ✅ Repositorio GitHub público/privado con el código
- ✅ Groq API Key (obtener en https://console.groq.com/keys)
- ✅ Cuenta en Render.com (gratuita)

---

## 🔧 Paso 1: Preparar GitHub

### 1.1 Hacer Push del Código

```bash
git add .
git commit -m "feat: add render.yaml for deployment"
git push origin main
```

### 1.2 Generar GitHub Personal Access Token (PAT)

Para que Render pueda desplegar automáticamente en cada push:

1. Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click en "Generate new token (classic)"
3. Dale nombre: `render-deployment`
4. Selecciona permisos:
   - `repo` (acceso completo a repositorios)
   - `workflow` (para CI/CD)
5. Copia el token (⚠️ solo se muestra una vez)

---

## 📱 Paso 2: Crear Cuenta en Render

### 2.1 Registro

1. Ve a https://render.com
2. Click en "Sign Up" → "Continue with GitHub"
3. Autoriza Render a acceder a tu GitHub
4. Completa tu perfil

### 2.2 Conectar Repositorio

1. En dashboard de Render → "New" → "Web Service"
2. Selecciona "Public Git Repository"
3. Ingresa: `https://github.com/incognauta/CatIA.git`
4. Click en "Connect"

---

## 🗄️ Paso 3: Crear PostgreSQL

### 3.1 Crear Instancia PostgreSQL

1. En Render Dashboard → "New" → "PostgreSQL"
2. Completa:
   - **Name:** `catia-db`
   - **Database:** `catia`
   - **User:** `catia_user`
   - **Region:** `Frankfurt` (o la más cercana a ti)
   - **PostgreSQL Version:** `15`
   - **Plan:** `Free` (Tier)

3. Click en "Create Database"

### 3.2 Copiar Credenciales

Después de creada, verás:
- **External Database URL** (importante - copiar completo):
  ```
  postgresql://user:password@hostname:5432/dbname
  ```

Guardaremos esto para el backend.

---

## ⚙️ Paso 4: Desplegar Backend

### 4.1 Crear Web Service para Backend

1. En Render Dashboard → "New" → "Web Service"
2. Conecta tu repositorio CatIA (si no está ya conectado)
3. Completa:

| Campo | Valor |
|-------|-------|
| **Name** | `catia-backend` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput` |
| **Start Command** | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30` |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Plan** | `Free` |
| **Region** | `Frankfurt` |

### 4.2 Agregar Variables de Entorno

Después de crear, ve a "Environment" y agrega:

```
DJANGO_SETTINGS_MODULE = config.settings.production
DEBUG = False
SECRET_KEY = (generar abajo ↓)
DATABASE_URL = (pegar URL de PostgreSQL)
GROQ_API_KEY = gsk_...
ALLOWED_HOSTS = catia-backend.onrender.com
CORS_ALLOWED_ORIGINS = https://catia-frontend.onrender.com
PYTHONUNBUFFERED = True
```

#### Generar SECRET_KEY

En tu terminal local:

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copiar el resultado y pegarlo en `SECRET_KEY`.

### 4.3 Desplegar

1. Click en "Manual Deploy" → "Deploy Latest Commit"
2. Esperar a que termine (verás logs en tiempo real)
3. Status debe cambiar a "Live" ✅

**URL del Backend:** `https://catia-backend.onrender.com`

---

## 🎨 Paso 5: Desplegar Frontend

### 5.1 Crear Web Service para Frontend

1. En Render Dashboard → "New" → "Web Service"
2. Conecta repositorio CatIA
3. Completa:

| Campo | Valor |
|-------|-------|
| **Name** | `catia-frontend` |
| **Environment** | `Node` |
| **Build Command** | `npm install --legacy-peer-deps && npm run build` |
| **Start Command** | `npm run preview` |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Plan** | `Free` |
| **Region** | `Frankfurt` |

### 5.2 Agregar Variable de Entorno

```
VITE_API_URL = https://catia-backend.onrender.com/api/v1
```

### 5.3 Desplegar

1. Click en "Manual Deploy" → "Deploy Latest Commit"
2. Esperar a que termine
3. Status debe cambiar a "Live" ✅

**URL del Frontend:** `https://catia-frontend.onrender.com`

---

## ✅ Paso 6: Verificar Despliegue

### 6.1 Verificar Backend

```bash
curl https://catia-backend.onrender.com/api/v1/health/
```

Debe responder:
```json
{"status": "ok"}
```

### 6.2 Verificar Base de Datos

En Render Dashboard → PostgreSQL → "Connect":

```bash
PGPASSWORD=tu_password psql -h hostname -U catia_user -d catia -c "\dt"
```

Debe listar las tablas de Django.

### 6.3 Verificar Frontend

1. Abre `https://catia-frontend.onrender.com` en el navegador
2. Debe cargar la aplicación React
3. Prueba: registrarse → crear notebook → subir documento → chatear con IA

---

## 🔄 CI/CD Automático

Render automáticamente redeploya cuando haces push a `main`:

```bash
# Hacer cambios
git add .
git commit -m "fix: improve chat performance"
git push origin main

# ✅ Render se da cuenta en ~10 segundos
# ✅ Inicia build automático
# ✅ Deploy en ~3-5 minutos
```

### Monitorear Deploy Automático

En Render Dashboard:
1. Click en el servicio (backend o frontend)
2. Ve a "Deployments"
3. Verás historial de deploys automáticos
4. Haz click en uno para ver logs detallados

---

## 📊 Monitoreo y Troubleshooting

### M1: Ver Logs en Tiempo Real

**Backend:**
```
Render Dashboard → catia-backend → Logs
```

Busca errores como:
- ❌ `ModuleNotFoundError` → Falta instalar paquete en requirements.txt
- ❌ `ProgrammingError` → Falta ejecutar migraciones
- ❌ `ConnectionRefusedError` → DATABASE_URL incorrecto

**Frontend:**
```
Render Dashboard → catia-frontend → Logs
```

### M2: Problemas Comunes

#### 🔴 Backend muestra "Internal Server Error"

1. Ve a Logs del backend
2. Busca el error específico
3. Soluciona y haz push a main
4. Render redeploya automáticamente

#### 🔴 Frontend no puede conectar al API

1. Verifica que `VITE_API_URL` esté correcto en frontend
2. Asegúrate de que backend esté "Live"
3. Revisa CORS en backend (variable `CORS_ALLOWED_ORIGINS`)

#### 🔴 Base de datos sin datos (migraciones no corrieron)

El Build Command ya lo hace:
```bash
python manage.py migrate --noinput
```

Pero si aun así no funciona:

1. Ve a PostgreSQL en Render
2. Click en "Connect"
3. Conéctate y ejecuta:
   ```sql
   \dt  -- Ver tablas
   ```

#### 🔴 Groq API Error

1. Verifica que `GROQ_API_KEY` esté correcto en backend → Environment
2. Comprueba que la API key sea válida: https://console.groq.com/keys
3. Revisa límites de rate limiting de Groq

### M3: Reiniciar Servicios

Si algo está atascado:

```
Render Dashboard → Servicio → Settings → "Manual Restart"
```

### M4: Escala de Free Tier

- ⏱️ Servicio se "duerme" después de 15 minutos sin actividad
- 🚀 Se reactiva cuando alguien accede (tarda ~30 segundos)
- 💾 PostgreSQL free: 100 MB (suficiente para testing)
- 🔄 Limite de deploy: 1 por minuto

Para producción: upgrade a plan pagado.

---

## 🎯 Próximos Pasos

Después del despliegue:

1. **Probar flujo completo:**
   - Registrarse
   - Crear notebook
   - Subir PDF
   - Chatear con IA

2. **Monitorear logs** en primeras 24 horas

3. **Configurar alertas** (opcional):
   - Render Dashboard → Settings → Notifications

4. **Escalar infraestructura** cuando sea necesario:
   - Aumentar workers en gunicorn
   - Upgrade PostgreSQL
   - Agregar Redis para cache

---

## 📞 Soporte

- **Render Docs:** https://render.com/docs
- **Django Docs:** https://docs.djangoproject.com
- **React Docs:** https://react.dev
- **Groq Docs:** https://console.groq.com/docs

