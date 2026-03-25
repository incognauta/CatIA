# 🚀 PRE-PUSH CHECKLIST - PDF_IA_Rework

## ✅ VERIFICACIONES CRÍTICAS

### 1. **SECRETOS & CREDENCIALES**
- [ ] NO hay `.env` files en staging (solo `.env.example`)
- [ ] NO hay API keys, tokens o credenciales en commits
- [ ] Verificar: `git diff --cached | grep -i "key\|secret\|token\|password"`
- [ ] Backend `.env` está en `.gitignore`
- [ ] Frontend `.env.local` está en `.gitignore`

### 2. **DEPENDENCIAS NO VERSIONADAS**
- [ ] NO hay `node_modules/` en staging
- [ ] NO hay `venv/` o `env/` en staging
- [ ] NO hay `__pycache__/` directories
- [ ] Verificar: `git ls-files | grep node_modules | wc -l` (debe ser 0)

### 3. **BUILD ARTIFACTS**
- [ ] NO hay `frontend/dist/` 
- [ ] NO hay `backend/build/` o `dist/`
- [ ] NO hay archivos `.egg-info/`

### 4. **ARCHIVOS GRANDES**
- [ ] Verificar tamaño total: `du -sh .git`
- [ ] Sin archivos > 50MB (Git LFS para más)
- [ ] Comando: `find . -size +50M -type f | grep -v node_modules`

### 5. **BASE DE DATOS & MEDIA**
- [ ] NO hay `db.sqlite3` o `*.db` files
- [ ] NO hay `/media/` o `/uploads/` directories
- [ ] NO hay `/data/embeddings/` o caches pesados

### 6. **DOCUMENTACIÓN**
- [ ] README.md actualizado con instrucciones
- [ ] `.env.example` files presentes y documentados
- [ ] GIT_STRATEGY.md explica qué se sube y qué no

---

## 📋 ESTRUCTURA FINAL ANTES DE PUSH

```
✅ DEBE EXISTIR:
backend/
├── requirements.txt
├── .env.example
├── manage.py
├── Dockerfile
└── apps/

frontend/
├── package.json
├── tsconfig.json
├── .env.example
└── src/

docker-compose.yml
README.md
GIT_STRATEGY.md
.gitignore
.env.example (raíz)

❌ NO DEBE EXISTIR:
backend/.env (secretos)
frontend/.env.local (secretos)
backend/__pycache__/
frontend/node_modules/
frontend/dist/
*.sqlite3
/data/embeddings/
```

---

## 🔍 COMANDOS DE VERIFICACIÓN

### Ver qué se va a subir
```bash
git add .
git status
```

### Ver archivos grandes que podrían ser problemáticos
```bash
git ls-files -o -i --exclude-standard | head -20
find . -size +10M -type f 2>/dev/null | grep -v ".git"
```

### Verificar qué archivos están tracked por git
```bash
git ls-files | wc -l  # número total de archivos
```

### Revisar último commit antes de push
```bash
git log -1 --name-status  # archivos modificados
git diff HEAD~1 --stat   # estadísticas de cambios
```

### Verificar nombres de secrets en archivos
```bash
git diff --cached | grep -iE "password|secret|key|token|api"
```

---

## 🛡️ VALIDACIÓN FINAL ANTES DE PUSH

```bash
# 1. Limpieza
git clean -fd  # Elimina archivos sin track

# 2. Status check
git status --short

# 3. Verify no secrets
git diff --cached | grep -i "password\|secret\|key" && echo "⚠️ SECRETOS ENCONTRADOS" || echo "✅ Sin secretos detectados"

# 4. Check file count and sizes
echo "📊 Total files:" && git ls-files | wc -l
echo "📊 Repo size:" && du -sh .git

# 5. List what will be pushed
git diff --cached --name-status | head -20

# 6. Final push (if all checks pass)
git push origin <branch-name>
```

---

## 🚨 SI ALGO SALE MAL

### Cancelar push antes de hacer
```bash
git reset HEAD~1  # Deshacer último commit (mantiene cambios)
git reset --hard HEAD~1  # Deshacer y perder cambios
```

### Si ya hiciste push con secretos
```bash
# OPCIÓN 1: Remover archivo del histórico (peligroso)
git rm --cached <archivo-secreto>
git commit --amend --no-edit
git push --force-with-lease

# OPCIÓN 2: Hacer un nuevo commit que borre los secretos
git rm <archivo-secreto>
git commit -m "Remove sensitive .env file"
git push

# OPCIÓN 3: Usar github.com/newren/git-filter-repo (más seguro)
# (Ver documentación)

# IMPORTANTE: Si subiste con secretos, REGENERA TODAS LAS CREDENCIALES
```

---

## 📝 TEMPLATE PARA FIRST COMMIT

```
Subject: Initial commit: PDF_IA MVP backend + frontend scaffold

- Backend: Django REST API with Groq integration
- Frontend: React 19 + Vite with authentication
- Database: PostgreSQL with pgvector
- Features: Notebooks, Chat, Document Upload

Closes #1
```

---

## ✨ DESPUÉS DEL PUSH

- [ ] Crear README.md completo si no existe
- [ ] Documentación de setup: "How to run locally"
- [ ] Add contributors
- [ ] Setup branch protection rules
- [ ] Configure CI/CD (GitHub Actions)

