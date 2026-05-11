#!/bin/bash

# PDF_IA_Rework Setup Script
# Automatiza la inicialización del proyecto de dos formas:
# 1. Docker Compose (Recomendado)
# 2. Local Development

set -e  # Exit on error

# Colors para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

# Check prerequisites
check_prerequisites() {
    print_header "Verificando Prerequisitos"
    
    if [ "$1" == "docker" ]; then
        if ! command -v docker &> /dev/null; then
            print_error "Docker no está instalado"
            exit 1
        fi
        print_success "Docker instalado"
        
        # Check both docker-compose (old) and docker compose (new)
        if command -v docker-compose &> /dev/null; then
            print_success "Docker Compose instalado (comando legacy: docker-compose)"
            DOCKER_COMPOSE_CMD="docker-compose"
        elif docker compose version &> /dev/null; then
            print_success "Docker Compose instalado (nuevo formato: docker compose)"
            DOCKER_COMPOSE_CMD="docker compose"
        else
            print_error "Docker Compose no está instalado"
            exit 1
        fi
    else
        if ! command -v python3 &> /dev/null; then
            print_error "Python 3 no está instalado"
            exit 1
        fi
        print_success "Python 3 instalado"
        
        if ! command -v node &> /dev/null; then
            print_error "Node.js no está instalado"
            exit 1
        fi
        print_success "Node.js instalado"
        
        if ! command -v npm &> /dev/null; then
            print_error "npm no está instalado"
            exit 1
        fi
        print_success "npm instalado"
    fi
}

# Setup Docker Compose
setup_docker() {
    print_header "Configuración Docker Compose"
    
    # Check if files exist
    if [ ! -f "backend/.env.example" ]; then
        print_error "No encontré backend/.env.example"
        exit 1
    fi
    
    if [ ! -f "frontend/.env.example" ]; then
        print_error "No encontré frontend/.env.example"
        exit 1
    fi
    
    # Create .env files if they don't exist
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        print_success "Creado backend/.env"
    else
        print_warning "backend/.env ya existe, no se sobrescribió"
    fi
    
    if [ ! -f "frontend/.env.local" ]; then
        cp frontend/.env.example frontend/.env.local
        print_success "Creado frontend/.env.local"
    else
        print_warning "frontend/.env.local ya existe, no se sobrescribió"
    fi
    
    # Handle API Keys
    print_header "Configuración de APIs"
    
    # Check if GROQ_API_KEY already exists
    if grep -q "GROQ_API_KEY=" backend/.env && [ "$(grep 'GROQ_API_KEY=' backend/.env | cut -d'=' -f2)" != "" ]; then
        print_success "GROQ_API_KEY detectada en backend/.env"
        print_info "Usando la key existente"
    else
        print_warning "GROQ_API_KEY no encontrada"
        read -p "¿Deseas configurarla ahora? (s/n): " configure_groq
        
        if [ "$configure_groq" == "s" ] || [ "$configure_groq" == "S" ]; then
            read -sp "Ingresa tu GROQ_API_KEY: " groq_key
            echo ""
            
            # Update .env file
            if grep -q "GROQ_API_KEY=" backend/.env; then
                sed -i.bak "s|GROQ_API_KEY=.*|GROQ_API_KEY=$groq_key|" backend/.env
            else
                echo "GROQ_API_KEY=$groq_key" >> backend/.env
            fi
            print_success "GROQ_API_KEY configurada en backend/.env"
        else
            print_warning "Sin GROQ_API_KEY, el chat con IA no funcionará"
            print_info "Obtén una gratis en: https://console.groq.com/keys"
            print_info "Puedes agregarla después en: backend/.env"
        fi
    fi
    
    # Add template for future APIs if not exists
    if ! grep -q "# Future API Keys" backend/.env; then
        cat >> backend/.env << 'EOF'

# ═══════════════════════════════════════════════════════════
# Future API Keys (agregar según sea necesario)
# ═══════════════════════════════════════════════════════════
# OPENAI_API_KEY=sk_...
# ANTHROPIC_API_KEY=sk-ant-...
# OTHER_API_KEY=...
EOF
        print_success "Template para futuras APIs agregado"
    fi
    
    # Start Docker Compose
    print_header "Iniciando Docker Compose"
    $DOCKER_COMPOSE_CMD up -d
    print_success "Servicios Docker iniciados"
    
    print_info "Esperando que los servicios se inicien (15 segundos)..."
    sleep 15
    
    print_header "✅ Setup Completado"
    echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
    echo -e "${GREEN}Backend API: http://localhost:8001/api/v1${NC}"
    echo -e "${GREEN}PostgreSQL: localhost:5434${NC}\n"
    
    # Try to open browser
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

# Setup Local Development
setup_local() {
    print_header "Configuración Desarrollo Local"
    
    # Backend setup
    print_info "Configurando Backend..."
    
    if [ ! -f "backend/.env.example" ]; then
        print_error "No encontré backend/.env.example"
        exit 1
    fi
    
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        print_success "Creado backend/.env"
    else
        print_warning "backend/.env ya existe"
    fi
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creando virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment creado"
    else
        print_warning "Virtual environment ya existe"
    fi
    
    # Activate venv
    print_info "Activando virtual environment..."
    source venv/bin/activate
    
    # Install requirements
    print_info "Instalando dependencias Python..."
    pip install -r requirements.txt -q
    print_success "Dependencias instaladas"
    
    # Migrate database
    print_info "Ejecutando migraciones..."
    python manage.py migrate
    print_success "Base de datos migrada"
    
    print_info "Backend listo. Para iniciarlo manualmente:"
    echo -e "${YELLOW}cd backend && source venv/bin/activate && python manage.py runserver 0.0.0.0:8001${NC}\n"
    
    cd ..
    
    # Frontend setup
    print_info "Configurando Frontend..."
    
    if [ ! -f "frontend/.env.example" ]; then
        print_error "No encontré frontend/.env.example"
        exit 1
    fi
    
    if [ ! -f "frontend/.env.local" ]; then
        cp frontend/.env.example frontend/.env.local
        print_success "Creado frontend/.env.local"
    else
        print_warning "frontend/.env.local ya existe"
    fi
    
    cd frontend
    
    # Install npm dependencies
    print_info "Instalando dependencias Node..."
    npm install --legacy-peer-deps -q
    print_success "Dependencias Node instaladas"
    
    print_info "Frontend listo. Para iniciarlo manualmente:"
    echo -e "${YELLOW}cd frontend && npm run dev${NC}\n"
    
    cd ..
    
    print_header "✅ Setup Completado"
    print_info "Para iniciar el proyecto:"
    echo -e "${YELLOW}Terminal 1:${NC} cd backend && source venv/bin/activate && python manage.py runserver 0.0.0.0:8001"
    echo -e "${YELLOW}Terminal 2:${NC} cd frontend && npm run dev"
    echo ""
    echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
    echo -e "${GREEN}Backend: http://localhost:8001/api/v1${NC}\n"
}

# Start script
print_header "PDF_IA_Rework - Setup Script"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Este script debe ejecutarse desde la raíz del proyecto"
    exit 1
fi

# Ask user which setup they want
echo "¿Cómo quieres iniciar el proyecto?"
echo ""
echo "1) Docker Compose (Recomendado - más fácil)"
echo "2) Local Development (Requiere Python + Node)"
echo ""
read -p "Selecciona opción (1 o 2): " choice

case $choice in
    1)
        check_prerequisites "docker"
        setup_docker
        ;;
    2)
        check_prerequisites "local"
        setup_local
        ;;
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

print_success "¡Listo para trabajar! 🚀"
