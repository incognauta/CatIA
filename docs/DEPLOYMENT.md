# 🚀 Deployment Guide

**Versión:** 1.0  
**Última actualización:** 21 de enero de 2025  
**Etapa:** Fase 7 Completa

Este documento describe las opciones de deployment para la aplicación CatIA.

---

## 📋 Tabla de Contenidos

1. [Development Setup](#development-setup)
2. [Docker Compose (Recomendado)](#docker-compose-recomendado)
3. [Production Deployment](#production-deployment)
4. [Environment Variables](#environment-variables)
5. [Troubleshooting](#troubleshooting)

---

## Development Setup

### Requisitos

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+ (local o Docker)
- Groq API Key (libre en https://console.groq.com/keys)

### Instalación Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Editar con tu GROQ_API_KEY

# Migraciones
python manage.py migrate

# Crear superuser (opcional)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver 0.0.0.0:8001

# En otra terminal - Frontend
cd frontend
npm install --legacy-peer-deps
cp .env.example .env.local
npm run dev
```

**Acceso:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001/api/v1
- Admin Django: http://localhost:8001/admin

---

## Docker Compose (Recomendado)

**Ventajas:**
- ✅ Ambiente aislado
- ✅ No requiere instalar Python/Node localmente
- ✅ PostgreSQL automático
- ✅ Un comando para todo
- ✅ Idéntico a producción

### Setup

```bash
# Copiar archivos de configuración
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Editar backend/.env con tu GROQ_API_KEY
nano backend/.env

# Construir (primera vez - ~2 minutos)
docker compose build --no-cache

# Iniciar servicios
docker compose up -d

# Verificar
docker compose ps
```

**Servicios:**
- PostgreSQL: puerto 5434
- Backend: puerto 8001
- Frontend: puerto 5173

### Usar la Aplicación

```bash
# Logs en tiempo real
docker compose logs -f

# Ejecutar migraciones
docker compose exec backend python manage.py migrate

# Crear superuser
docker compose exec backend python manage.py createsuperuser

# Acceder a shell de Django
docker compose exec backend python manage.py shell

# Detener servicios
docker compose down

# Limpiar volúmenes (CUIDADO - borra datos)
docker compose down -v
```

---

## Production Deployment

### Opción 1: Render (Recomendado para principiantes)

```bash
# 1. Crear cuenta en https://render.com
# 2. Conectar repositorio GitHub
# 3. Crear Web Service:
#    - Name: catia-backend
#    - Runtime: Python 3.12
#    - Build Command: pip install -r requirements.txt
#    - Start Command: gunicorn config.wsgi -b 0.0.0.0:8001
# 4. Agregar variables de entorno
# 5. Conectar PostgreSQL en Render (add-on)
# 6. Deploy automático en cada push a main
```

### Opción 2: AWS EC2 + RDS

```bash
# EC2: Ubuntu 24.04 LTS
# 1. SSH a instancia
ssh -i key.pem ubuntu@your-instance-ip

# 2. Instalar dependencias
sudo apt update && sudo apt install -y python3.12 python3.12-venv nodejs npm postgresql-client

# 3. Clonar repositorio
git clone https://github.com/incognauta/CatIA.git
cd CatIA/backend

# 4. Setup backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 5. Configurar .env con RDS endpoint

# 6. Migraciones
python manage.py migrate

# 7. Crear systemd service
sudo nano /etc/systemd/system/catia.service
```

**Systemd service template:**

```ini
[Unit]
Description=CatIA Django Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/CatIA/backend
ExecStart=/home/ubuntu/CatIA/backend/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8001 \
    config.wsgi
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable catia
sudo systemctl start catia
```

### Opción 3: Docker + Kubernetes (Avanzado)

```bash
# Construir imágenes personalizadas
docker build -t my-registry/catia-backend:1.0 ./backend
docker build -t my-registry/catia-frontend:1.0 ./frontend

# Push a registry (Docker Hub, ECR, etc)
docker push my-registry/catia-backend:1.0
docker push my-registry/catia-frontend:1.0

# Desplegar en Kubernetes con helm o kubectl
kubectl apply -f k8s/deployment.yaml
```

---

## Environment Variables

### Backend (.env)

```ini
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# PostgreSQL
DB_ENGINE=postgresql
DB_NAME=catia_db
DB_USER=catia_user
DB_PASSWORD=strong_password_here
DB_HOST=db
DB_PORT=5432

# Groq API
GROQ_API_KEY=gsk_your_api_key_here

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256

# Email (opcional para reset password)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# O usar SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
```

### Frontend (.env.local)

```ini
VITE_API_URL=http://localhost:8001/api/v1
VITE_APP_NAME=CatIA
```

**En producción (frontend/.env.production):**

```ini
VITE_API_URL=https://api.your-domain.com/api/v1
VITE_APP_NAME=CatIA
```

---

## SSL/HTTPS (Producción)

### Con Let's Encrypt + Nginx

```bash
# En el servidor
sudo apt install certbot python3-certbot-nginx

# Generar certificado
sudo certbot certonly --nginx -d your-domain.com

# Nginx config
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}

# Renovación automática
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Database Backups

### Manual Backup

```bash
# Con PostgreSQL local
pg_dump catia_db > backup_$(date +%Y%m%d).sql

# Restaurar
psql catia_db < backup_20250121.sql

# Con Docker
docker compose exec -T postgres pg_dump -U catia_user catia_db > backup.sql
```

### Backup Automático (Cron)

```bash
# Agregar a crontab
0 2 * * * pg_dump catia_db > /backups/catia_$(date +\%Y\%m\%d).sql

# Limpiar backups viejos (>30 días)
find /backups -name "catia_*.sql" -mtime +30 -delete
```

---

## Monitoreo

### Logging

```bash
# Django logs
docker compose logs backend | grep ERROR

# Frontend logs (browser console)
# DevTools → Console

# PostgreSQL logs
docker compose logs postgres
```

### Health Check

```bash
# Backend
curl http://localhost:8001/api/v1/health/

# Frontend
curl http://localhost:5173/
```

---

## Performance Tips

### Backend
- Use Gunicorn con 4-8 workers (CPU cores * 2)
- Enable caching con Redis
- Use async views para Groq API
- Database connection pooling con pgBouncer

### Frontend
- Build optimizado: `npm run build`
- Compresión gzip habilitada
- Lazy loading de componentes
- Service workers (PWA)

### Database
- Índices en campos de búsqueda frecuente
- Connection pooling
- Backups automáticos
- Query optimization con EXPLAIN ANALYZE

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Puerto 8001 en uso | `lsof -i :8001` → `kill -9 PID` |
| Docker error "refused to connect" | Esperar 10s, reintentar: `docker compose restart` |
| Migraciones fallan | `docker compose down -v` → rebuild |
| API 500 | Verificar logs: `docker compose logs backend` |
| CORS errors | Revisar `CORS_ALLOWED_ORIGINS` en .env |
| PostgreSQL no conecta | Verificar credenciales y puerto |
| Groq API rate limit | Esperar 5 minutos, reintentar |

---

## Escala (Futuro)

```
Fase 1: Monolito (Actual)
↓
Fase 2: Microservicios
  - API Gateway
  - Auth Service
  - Chat Service
  - Document Service
↓
Fase 3: Serverless
  - AWS Lambda para procesamiento
  - API Gateway
  - RDS Aurora Serverless
↓
Fase 4: Global
  - CDN para frontend
  - Replicas de BD en múltiples regiones
  - Load balancing
```

---

## Notas de Seguridad

- ⚠️ Nunca commitear .env a git
- ⚠️ Usar secrets manager (AWS Secrets Manager, Vault)
- ⚠️ HTTPS obligatorio en producción
- ⚠️ Rate limiting en endpoints públicos
- ⚠️ Validación de input en frontend y backend
- ⚠️ CSRF tokens para formularios
- ⚠️ SQL injection prevention con ORM
- ⚠️ Regular security audits

---

## Contacto & Soporte

- 📧 Email: support@catia.app
- 🐛 Issues: https://github.com/incognauta/CatIA/issues
- 📚 Docs: [README.md](README.md)
- 📊 Status: [ESTADO_PROYECTO.md](docs/ESTADO_PROYECTO.md)

---

Última revisión: 21 de enero de 2025
