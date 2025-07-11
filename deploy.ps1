# Script de Despliegue para Windows PowerShell
Write-Host "🚀 Despliegue Rápido - Separador de Audio IA" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: No se encontró package.json. Asegúrate de estar en el directorio raíz del proyecto." -ForegroundColor Red
    exit 1
}

# Función para mostrar menú
function Show-Menu {
    Write-Host ""
    Write-Host "🎯 Selecciona tu plataforma de despliegue:" -ForegroundColor Yellow
    Write-Host "1) Railway (Recomendado)" -ForegroundColor Cyan
    Write-Host "2) Render" -ForegroundColor Cyan
    Write-Host "3) VPS con Docker" -ForegroundColor Cyan
    Write-Host "4) Google Cloud Run" -ForegroundColor Cyan
    Write-Host "5) Salir" -ForegroundColor Cyan
    Write-Host ""
    $choice = Read-Host "Ingresa tu opción (1-5)"
    return $choice
}

# Función para Railway
function Deploy-Railway {
    Write-Host "🚂 Desplegando en Railway..." -ForegroundColor Green
    
    # Verificar si Railway CLI está instalado
    try {
        railway --version | Out-Null
    } catch {
        Write-Host "📦 Instalando Railway CLI..." -ForegroundColor Yellow
        npm install -g @railway/cli
    }
    
    # Login y despliegue
    Write-Host "🔐 Iniciando sesión en Railway..." -ForegroundColor Yellow
    railway login
    
    Write-Host "🚀 Desplegando aplicación..." -ForegroundColor Yellow
    railway up
    
    Write-Host "✅ ¡Despliegue completado! Tu app estará disponible en Railway." -ForegroundColor Green
}

# Función para Render
function Deploy-Render {
    Write-Host "🌊 Desplegando en Render..." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Pasos para Render:" -ForegroundColor Yellow
    Write-Host "1. Ve a https://render.com" -ForegroundColor White
    Write-Host "2. Conecta tu repositorio de GitHub" -ForegroundColor White
    Write-Host "3. Selecciona 'Web Service'" -ForegroundColor White
    Write-Host "4. Configura:" -ForegroundColor White
    Write-Host "   - Build Command: npm install && npm run build" -ForegroundColor Gray
    Write-Host "   - Start Command: npm start" -ForegroundColor Gray
    Write-Host "   - Environment: Node" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔗 Tu app estará disponible en: https://tu-app.onrender.com" -ForegroundColor Green
}

# Función para VPS con Docker
function Deploy-VPS {
    Write-Host "🐳 Desplegando en VPS con Docker..." -ForegroundColor Green
    
    # Verificar si Docker está instalado
    try {
        docker --version | Out-Null
    } catch {
        Write-Host "📦 Docker no está instalado. Instala Docker Desktop desde:" -ForegroundColor Red
        Write-Host "https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
    
    # Construir y ejecutar
    Write-Host "🔨 Construyendo imagen Docker..." -ForegroundColor Yellow
    docker-compose build
    
    Write-Host "🚀 Iniciando servicios..." -ForegroundColor Yellow
    docker-compose up -d
    
    Write-Host "✅ ¡Despliegue completado! Tu app estará disponible en http://localhost:5000" -ForegroundColor Green
    Write-Host "📊 Para ver logs: docker-compose logs -f" -ForegroundColor Gray
}

# Función para Google Cloud Run
function Deploy-GCloud {
    Write-Host "☁️ Desplegando en Google Cloud Run..." -ForegroundColor Green
    
    # Verificar si gcloud está instalado
    try {
        gcloud --version | Out-Null
    } catch {
        Write-Host "📦 Google Cloud CLI no está instalado." -ForegroundColor Red
        Write-Host "Visita: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
        exit 1
    }
    
    # Desplegar
    Write-Host "🚀 Desplegando aplicación..." -ForegroundColor Yellow
    gcloud run deploy audio-separator --source . --platform managed --region us-central1 --allow-unauthenticated
    
    Write-Host "✅ ¡Despliegue completado!" -ForegroundColor Green
}

# Función principal
function Main {
    do {
        $choice = Show-Menu
        
        switch ($choice) {
            "1" {
                Deploy-Railway
                break
            }
            "2" {
                Deploy-Render
                break
            }
            "3" {
                Deploy-VPS
                break
            }
            "4" {
                Deploy-GCloud
                break
            }
            "5" {
                Write-Host "👋 ¡Hasta luego!" -ForegroundColor Green
                exit 0
            }
            default {
                Write-Host "❌ Opción inválida. Intenta de nuevo." -ForegroundColor Red
            }
        }
    } while ($true)
}

# Ejecutar función principal
Main 