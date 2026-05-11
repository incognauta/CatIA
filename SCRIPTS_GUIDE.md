# Guía de Scripts de Inicio

Este proyecto incluye dos scripts `.sh` que automatizan la configuración e inicio del proyecto.

## 📋 Requisitos Previos

- **Bash** (incluido en Linux y macOS)
- Para **Docker Compose**: Docker y Docker Compose instalados
- Para **Local Development**: Python 3.11+, Node.js 18+ y npm

---

## 🚀 Paso 1: Configuración Inicial (`setup.sh`)

### ¿Qué hace?
- Verifica que tengas los prerequisitos instalados
- Copia archivos `.env` de ejemplo
- Configura variables de entorno
- Prepara la base de datos
- Instala dependencias

### ¿Cuándo usarlo?
**Una sola vez** al principio o después de clonar el proyecto.

### Cómo ejecutarlo

```bash
cd PDF_IA_Rework
./setup.sh
```

### ¿Qué te preguntará?

1. **Opción de inicio:**
   ```
   1) Docker Compose (Recomendado - más fácil)
   2) Local Development (Requiere Python + Node)
   ```

2. **Si eliges Docker:**
   - Te pedirá tu GROQ_API_KEY
   - Iniciará automáticamente todos los servicios
   - **Listo en ~2 minutos** ⚡

3. **Si eliges Local:**
   - Crea virtual environment Python
   - Instala dependencias (puede tardar 5-10 min)
   - Te dice cómo iniciar manualmente

---

## ⚡ Paso 2: Inicio Rápido (`start.sh`)

### ¿Qué hace?
- Inicia Backend y Frontend automáticamente
- Solo funciona después de correr `setup.sh`

### ¿Cuándo usarlo?
**Cada vez que quieras desarrollar** (después del primer setup).

### Cómo ejecutarlo

```bash
./start.sh
```

### Comportamiento

#### Opción 1: Docker Compose
```bash
$ ./start.sh
¿Deseas usar Docker Compose? (s/n): s
Iniciando Docker Compose...
```
✅ Se inician todos los servicios en contenedores

#### Opción 2: Local Development
```bash
$ ./start.sh
Iniciando Backend...
✓ Virtual environment activado
✓ Backend iniciado (PID: 12345)

Iniciando Frontend...
✓ Frontend iniciado (PID: 12346)

✅ Servicios Iniciados
Frontend: http://localhost:5173
Backend:  http://localhost:8001/api/v1

Presiona Ctrl+C para detener ambos servicios
```

---

## 📊 Comparación de Opciones

| Aspecto | Docker Compose | Local Development |
|---------|---|---|
| **Setup inicial** | ⚡ Rápido (2 min) | ⏱️ Lento (10 min) |
| **Inicio (start.sh)** | ⚡ Rápido | ⚡ Rápido |
| **Dependencies** | Docker, Docker Compose | Python, Node.js |
| **Recomendado para** | Principiantes, rápido desarrollo | Control total |
| **Problemas de puerto** | Menos comunes | Requiere revisión |
| **Updates** | Reconstruir imagen | Manualmente |

---

## 🔧 Uso Manual (Sin Scripts)

Si prefieres hacerlo manualmente:

### Docker Compose
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# Edita backend/.env y agrega tu GROQ_API_KEY
docker-compose up -d
```

### Local
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001

# Frontend (en otra terminal)
cd frontend
npm install --legacy-peer-deps
npm run dev
```

---

## ✅ Checklist Después de Setup

- [ ] `./setup.sh` ejecutado correctamente
- [ ] Los archivos `.env` fueron creados
- [ ] GROQ_API_KEY está configurada (si usas Docker)
- [ ] Puedes acceder a http://localhost:5173 (Frontend)
- [ ] Puedes acceder a http://localhost:8001/api/v1 (Backend)

---

## 🆘 Troubleshooting

### Error: "Permission denied" al ejecutar scripts

```bash
chmod +x setup.sh start.sh
```

### Error: Puerto ya en uso

**Para Docker:**
```bash
docker-compose down
docker-compose up -d
```

**Para Local:**
```bash
# Cambia los puertos en .env o en el comando:
python manage.py runserver 0.0.0.0:8002
npm run dev -- --port 5174
```

### Error: GROQ_API_KEY no configurada

```bash
nano backend/.env
# Agrega: GROQ_API_KEY=gsk_...
# Guarda con Ctrl+X, Y, Enter
```

### Error: Virtual environment no existe

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📱 URLs de Acceso

Una vez que los servicios están corriendo:

| Servicio | URL |
|----------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8001/api/v1 |
| **Django Admin** | http://localhost:8001/admin |
| **PostgreSQL** | localhost:5434 (local: no aplica) |

---

## 🎯 Flujo Típico

### Primer día

```bash
# 1. Clonar proyecto
git clone <repo>
cd PDF_IA_Rework

# 2. Setup inicial (solo una vez)
./setup.sh
# → Elige Docker Compose o Local
# → Espera a que termine

# 3. Eso es todo! El proyecto está listo
```

### Días siguientes

```bash
# Simple: Inicia servicios
./start.sh

# Abre http://localhost:5173
# ¡A desarrollar!
```

---

## 💡 Tips Útiles

### Limpiar datos (Docker)
```bash
docker-compose down -v
./setup.sh
```

### Ver logs (Docker)
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Detener servicios sin borrar datos (Docker)
```bash
docker-compose stop
```

### Crear superuser Django
```bash
# Si usas Docker
docker-compose exec backend python manage.py createsuperuser

# Si usas Local
cd backend && source venv/bin/activate
python manage.py createsuperuser
```

---

## 🚀 ¡Listo!

Ya tienes todo automatizado. Solo ejecuta:

```bash
./setup.sh   # Una sola vez
./start.sh   # Cada vez que quieras desarrollar
```

¿Preguntas? Revisa el README principal.
