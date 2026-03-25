# 📋 Git Ignore Strategy - PDF_IA_Rework

## ✅ QUÉ SÍ SE SUBE

- ✅ Código fuente (Python, TypeScript, CSS)
- ✅ Archivos de configuración (tsconfig.json, pyproject.toml, etc.)
- ✅ Documentación (README.md, docs/)
- ✅ Docker compose files (docker-compose.yml)
- ✅ Archivos de entrada de datos de ejemplo (.sample)
- ✅ .github/ workflows (CI/CD)

---

## ❌ QUÉ NO SE SUBE (Y POR QUÉ)

### 🔐 **SECRETS & CREDENTIALS**
```
.env, .env.local, *.key, *.pem, secrets.json
```
❌ **Nunca** subas credenciales, API keys o tokens
- Backend `.env` (GROQ_API_KEY, DATABASE_URL, SECRET_KEY)
- Frontend `.env.local` (API_BASE_URL con datos sensibles)

### 📦 **DEPENDENCIAS GENERADAS**
```
node_modules/, venv/, __pycache__/
```
❌ Son pesadas (1GB+) y se regeneran con `npm install` / `pip install`
- Otros desarrolladores instalan fresh desde package.json / requirements.txt

### 🏗️ **BUILD ARTIFACTS**
```
/frontend/dist/, /frontend/build/
/backend/dist/, /backend/build/
```
❌ Se generan al hacer build. No van al repo.

### 📊 **DATABASE & MEDIA**
```
*.sqlite3, /media/, /uploads/, /data/
```
❌ Archivos de base de datos locales y uploads de usuarios
- No incluyen datos sensibles o personales

### 🧠 **CACHE & EMBEDDINGS**
```
embeddings_cache/, ai_logs/, llm_cache/
/notebooks/embeddings/
```
❌ Cachés de IA y modelos grandes (muy pesados)
- Se regeneran según sea necesario

### 🔧 **IDE & OS FILES**
```
.vscode/, .idea/, .DS_Store, Thumbs.db
```
❌ Configuración local del IDE (no relevante para otros devs)

### 🧪 **TESTS & COVERAGE**
```
.pytest_cache/, htmlcov/, coverage.xml
```
❌ Archivos generados durante testing

---

## 📝 ESTRUCTURA RECOMENDADA PARA SUBIR

```
PDF_IA_Rework/
├── backend/
│   ├── apps/
│   ├── config/
│   ├── manage.py
│   ├── requirements.txt          ✅ (sí)
│   ├── Dockerfile               ✅ (sí)
│   ├── .env.example             ✅ (sí - ejemplo)
│   └── .env                     ❌ (NO - secretos)
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json             ✅ (sí)
│   ├── vite.config.ts           ✅ (sí)
│   ├── tsconfig.json            ✅ (sí)
│   ├── .gitignore               ✅ (sí)
│   ├── node_modules/            ❌ (NO - demasiado grande)
│   └── dist/                    ❌ (NO - se genera con build)
│
├── docker-compose.yml           ✅ (sí)
├── README.md                    ✅ (sí)
├── .gitignore                   ✅ (sí)
└── .env.example                 ✅ (sí - para docs)
```

---

## 🛡️ ANTES DE HACER PUSH - CHECKLIST

- [ ] ¿Hay `.env` files? → Renombrar a `.env.example` y agregar un template
- [ ] ¿Hay `node_modules/`? → Debería estar en .gitignore
- [ ] ¿Hay `venv/`? → Debería estar en .gitignore
- [ ] ¿Hay archivos grandes (>50MB)? → Usar Git LFS si es necesario
- [ ] ¿Hay keys o tokens expuestos en el código? → Removerlos inmediatamente
- [ ] ¿El README.md explica cómo configurar .env.example? → Sí
- [ ] ¿Está subido `docker-compose.yml` con todas las configuraciones? → Sí

---

## 🚀 COMANDOS ÚTILES ANTES DEL PUSH

```bash
# Ver qué archivos se van a subir
git status

# Ver qué archivos git tiene tracked (útil para debug)
git ls-files | head -20

# Verificar qué sería ignorado
git check-ignore -v *

# Agregar todo EXCEPTO archivos ignorados
git add .

# Verificar cambios antes de commit
git diff --cached
```

---

## 📌 ESPECIAL: CREAR .env.example

En lugar de subir `.env` real, crea `.env.example`:

### Backend `backend/.env.example`
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost/dbname
CORS_ALLOWED_ORIGINS=http://localhost:5173
GROQ_API_KEY=<obtén esto de https://console.groq.com>
```

### Frontend `frontend/.env.example`
```bash
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

---

## ⚠️ SI ACCIDENTALMENTE SUBISTE SECRETS

```bash
# Para QUITAR un archivo del histórico (peligroso)
git rm --cached .env
git commit --amend --no-edit
git push --force-with-lease

# MEJOR: Usa git-filter-repo o github.com/newren/git-filter-repo
# (más seguro para el histórico completo)
```

