#!/bin/bash

echo "🚀 Despliegue Rápido - Separador de Audio IA"
echo "=============================================="

# Verificar si estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Función para mostrar menú
show_menu() {
    echo ""
    echo "🎯 Selecciona tu plataforma de despliegue:"
    echo "1) Railway (Recomendado)"
    echo "2) Render"
    echo "3) VPS con Docker"
    echo "4) Google Cloud Run"
    echo "5) Salir"
    echo ""
    read -p "Ingresa tu opción (1-5): " choice
}

# Función para Railway
deploy_railway() {
    echo "🚂 Desplegando en Railway..."
    
    # Verificar si Railway CLI está instalado
    if ! command -v railway &> /dev/null; then
        echo "📦 Instalando Railway CLI..."
        npm install -g @railway/cli
    fi
    
    # Login y despliegue
    echo "🔐 Iniciando sesión en Railway..."
    railway login
    
    echo "🚀 Desplegando aplicación..."
    railway up
    
    echo "✅ ¡Despliegue completado! Tu app estará disponible en Railway."
}

# Función para Render
deploy_render() {
    echo "🌊 Desplegando en Render..."
    echo ""
    echo "📋 Pasos para Render:"
    echo "1. Ve a https://render.com"
    echo "2. Conecta tu repositorio de GitHub"
    echo "3. Selecciona 'Web Service'"
    echo "4. Configura:"
    echo "   - Build Command: npm install && npm run build"
    echo "   - Start Command: npm start"
    echo "   - Environment: Node"
    echo ""
    echo "🔗 Tu app estará disponible en: https://tu-app.onrender.com"
}

# Función para VPS
deploy_vps() {
    echo "🐳 Desplegando en VPS con Docker..."
    
    # Verificar si Docker está instalado
    if ! command -v docker &> /dev/null; then
        echo "📦 Instalando Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        sudo usermod -aG docker $USER
        echo "🔄 Reinicia tu sesión para aplicar los cambios de Docker"
        exit 1
    fi
    
    # Construir y ejecutar
    echo "🔨 Construyendo imagen Docker..."
    docker-compose build
    
    echo "🚀 Iniciando servicios..."
    docker-compose up -d
    
    echo "✅ ¡Despliegue completado! Tu app estará disponible en http://localhost:5000"
    echo "📊 Para ver logs: docker-compose logs -f"
}

# Función para Google Cloud Run
deploy_gcloud() {
    echo "☁️ Desplegando en Google Cloud Run..."
    
    # Verificar si gcloud está instalado
    if ! command -v gcloud &> /dev/null; then
        echo "📦 Instalando Google Cloud CLI..."
        echo "Visita: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Desplegar
    echo "🚀 Desplegando aplicación..."
    gcloud run deploy audio-separator \
        --source . \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated
    
    echo "✅ ¡Despliegue completado!"
}

# Función principal
main() {
    while true; do
        show_menu
        
        case $choice in
            1)
                deploy_railway
                break
                ;;
            2)
                deploy_render
                break
                ;;
            3)
                deploy_vps
                break
                ;;
            4)
                deploy_gcloud
                break
                ;;
            5)
                echo "👋 ¡Hasta luego!"
                exit 0
                ;;
            *)
                echo "❌ Opción inválida. Intenta de nuevo."
                ;;
        esac
    done
}

# Ejecutar función principal
main 