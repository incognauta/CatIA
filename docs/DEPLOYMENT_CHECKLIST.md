# ✅ Checklist Pre-Deployment a Render

Antes de iniciar el despliegue, asegúrate de cumplir todos estos puntos.

---

## 📋 Requisitos

### Cuentas & Accesos
- [ ] Cuenta en GitHub (con el código en un repositorio)
- [ ] Cuenta en Render.com (registrate con GitHub)
- [ ] Groq API Key (obtener en https://console.groq.com/keys)

### Código Local
- [ ] Todos los cambios están commiteados (`git status` debe estar limpio)
- [ ] Último commit hecho: `git push origin main`
- [ ] Repository público o Render tiene acceso

---

## 🔍 Verificaciones Técnicas

### Backend

- [ ] Archivo `backend/.env.example` existe y está actualizado
- [ ] `backend/requirements.txt` contiene todas las dependencias:
  - [ ] Django 5.0+
  - [ ] djangorestframework
  - [ ] djangorestframework-simplejwt
  - [ ] gunicorn
  - [ ] dj-database-url
  - [ ] python-decouple
  - [ ] groq
  - [ ] PyPDF2, pdf2image, python-docx, pytesseract (procesamiento)

Verificar:
```bash
grep -E "Django|gunicorn|dj-database|groq" backend/requirements.txt
```

- [ ] `backend/config/urls.py` tiene health check en `/health/`
- [ ] `backend/config/settings/production.py` existe y es básico
- [ ] `backend/config/settings/base.py` tiene `SECRET_KEY` configurable
- [ ] `backend/Dockerfile` existe y es compatible

Verificar:
```bash
# Ver si hay referencias a hardcoded settings
grep -r "settings.development" backend/
# Debe estar vacío o usar config.settings.production
```

### Frontend

- [ ] `frontend/package.json` existe y tiene scripts:
  - [ ] `npm run build` — Build for production
  - [ ] `npm run preview` — Preview production build

Verificar:
```bash
grep -A 5 '"scripts"' frontend/package.json | grep -E "build|preview"
```

- [ ] `frontend/.env.example` existe
- [ ] `frontend/vite.config.ts` o `vite.config.js` existe
- [ ] `frontend/src/main.tsx` o `src/main.jsx` existe

### Database

- [ ] PostgreSQL versión 15+ disponible (Render lo proporciona)
- [ ] Migraciones de Django existen:
  ```bash
  ls backend/apps/*/migrations/
  # Debe listar archivos como 0001_initial.py, etc.
  ```

---

## 📁 Estructura de Archivos

```
✅ Debe existir:
├── render.yaml                          # Orquestación de servicios
├── backend/
│   ├── requirements.txt                 # Dependencias
│   ├── .env.example                     # Template de env vars
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py            # Mínimo pero existe
│   │   ├── urls.py                      # Con /health/
│   │   └── wsgi.py
│   ├── apps/
│   │   └── */migrations/*.py            # Migraciones
│   └── Dockerfile
└── frontend/
    ├── package.json                     # Con scripts build & preview
    ├── .env.example
    ├── vite.config.ts/js
    ├── tsconfig.json
    ├── Dockerfile
    └── src/
        └── main.tsx/jsx
```

Verificar:
```bash
cd /home/incognauta/Escritorio/IA/PDF_IA_Rework
ls -la render.yaml backend/requirements.txt frontend/package.json
# Todos deben existir
```

---

## 🔐 Seguridad

- [ ] ⚠️ NO pusheaste `.env` a GitHub (solo `.env.example`)
- [ ] ⚠️ NO pusheaste secrets o API keys
- [ ] ⚠️ `DEBUG=False` en `production.py`

Verificar:
```bash
# Buscar secrets en el código
grep -r "gsk_" backend/ frontend/  # GROQ keys
grep -r "SECRET_KEY.*=" backend/   # Hardcoded secrets
# Deben retornar vacío o solo en .env.example
```

---

## ✨ Características Implementadas

- [ ] Sistema de autenticación (JWT) funcionando localmente
- [ ] Endpoints de notebook CRUD funcionando
- [ ] Upload de documentos funcionando
- [ ] Chat con IA funcionando
- [ ] React app compilando sin errores

Verificar (local):
```bash
# Backend
cd backend
python manage.py check
# Debe decir: "System check identified no issues (0 silenced)."

# Frontend
cd ../frontend
npm run build
# Debe compilar sin errores críticos
```

---

## 📋 Documentación Actualizada

- [ ] Existe `docs/RENDER_DEPLOYMENT.md` (paso a paso)
- [ ] Existe `docs/RENDER_ENV_REFERENCE.md` (valores de env)
- [ ] README.md menciona opción de Render para despliegue

---

## 🎯 Antes de Hacer Click "Deploy" en Render

Tienes preparados:
- [ ] GitHub Personal Access Token (para CI/CD automático)
- [ ] Groq API Key copiad al clipboard
- [ ] DATABASE_URL de PostgreSQL (después de crear en Render)
- [ ] Dominio del backend: `catia-backend` (lo genera Render)
- [ ] Dominio del frontend: `catia-frontend` (lo genera Render)

---

## 🚨 Si Algo Falla

Antes de contactar soporte:

1. **Revisa los Logs:**
   ```
   Render Dashboard → Servicio → Logs
   ```

2. **Errores comunes:**
   - `ModuleNotFoundError` → Falta en `requirements.txt` o `package.json`
   - `ProgrammingError` → Migraciones no corrieron, revisa Build Command
   - `ConnectionRefusedError` → DATABASE_URL incorrecto
   - `403 Forbidden` → CORS mal configurado o ALLOWED_HOSTS incorrecto

3. **Redeploya manualmente:**
   ```
   Render Dashboard → Servicio → Manual Deploy → Deploy Latest Commit
   ```

4. **Reinicia el servicio:**
   ```
   Render Dashboard → Servicio → Settings → Manual Restart
   ```

---

## 📞 Recursos

- **Render Docs:** https://render.com/docs/deploy-django
- **Django Docs:** https://docs.djangoproject.com/en/5.0/
- **Vite Docs:** https://vitejs.dev/
- **Issues/Soporte:** GitHub Issues en incognauta/CatIA

