#!/bin/bash

# PDF_IA_Rework Quick Start
# Inicia backend y frontend automáticamente (solo después de correr setup.sh)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Function to open browser
open_browser() {
    print_info "Abriendo navegador..."
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:5173" &
        print_success "Navegador abierto en http://localhost:5173"
    elif command -v open &> /dev/null; then
        open "http://localhost:5173" &
        print_success "Navegador abierto en http://localhost:5173"
    else
        print_warning "No se pudo abrir el navegador automáticamente"
        print_info "Abre manualmente: http://localhost:5173"
    fi
}

# Check if setup has been run
if [ ! -f "backend/.env" ] && [ ! -f "docker-compose.yml" ]; then
    print_error "Primero ejecuta: ./setup.sh"
    exit 1
fi

# Detect docker-compose command (old vs new format)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"  # fallback
fi

print_header "PDF_IA_Rework - Quick Start"

# Detect which setup was used
if command -v docker &> /dev/null && [ -f "docker-compose.yml" ]; then
    read -p "¿Deseas usar Docker Compose? (s/n, default=s): " use_docker
    use_docker=${use_docker:-s}
    
    if [ "$use_docker" == "s" ] || [ "$use_docker" == "S" ]; then
        print_info "Iniciando Docker Compose..."
        $DOCKER_COMPOSE_CMD up -d
        print_success "Servicios Docker iniciados"
        
        print_info "Esperando que los servicios estén listos (10 segundos)..."
        sleep 10
        
        print_header "✅ Servicios Iniciados"
        echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
        echo -e "${GREEN}Backend:  http://localhost:8001/api/v1${NC}"
        echo ""
        
        # Open browser
        sleep 2
        open_browser
        
        print_info "Los servicios están corriendo en background"
        print_info "Para detenerlos: docker compose down"
        exit 0
    fi
fi

# Local development mode
print_info "Iniciando modo desarrollo local..."
echo ""
print_warning "Se iniciarán Backend y Frontend"
print_warning "Usa Ctrl+C para detener todos los servicios"
echo ""

# Backend
print_info "Iniciando Backend..."
cd backend

if [ ! -d "venv" ]; then
    print_error "Virtual environment no existe. Ejecuta: ./setup.sh"
    exit 1
fi

source venv/bin/activate
print_success "Virtual environment activado"

# Start backend in background
python manage.py runserver 0.0.0.0:8001 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
print_success "Backend iniciado (PID: $BACKEND_PID)"

cd ..

# Wait for backend to start
print_info "Esperando que Backend esté listo..."
sleep 3

# Frontend
print_info "Iniciando Frontend..."
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
print_success "Frontend iniciado (PID: $FRONTEND_PID)"

cd ..

# Wait for frontend to start
print_info "Esperando que Frontend esté listo..."
sleep 5

print_header "✅ Servicios Iniciados"
echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}Backend:  http://localhost:8001/api/v1${NC}"
echo ""
print_warning "Presiona Ctrl+C para detener ambos servicios"
echo ""

# Open browser
open_browser
echo ""

# Trap to kill both processes on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; print_info 'Servicios detenidos'; exit" SIGINT

# Wait for both processes
wait
