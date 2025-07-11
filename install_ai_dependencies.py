#!/usr/bin/env python3
"""
Script de instalación para dependencias de IA de separación de audio
"""
import subprocess
import sys
import os

def install_package(package):
    """Instala un paquete usando pip"""
    try:
        print(f"Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        return False

def main():
    print("🎵 Configurando dependencias de IA para separación de audio...")
    print("=" * 60)
    
    # Lista de paquetes core
    core_packages = [
        "librosa==0.10.1",
        "soundfile==0.12.1", 
        "numpy==1.24.3",
        "scipy==1.11.4",
        "psutil==5.9.6",
        "pydub==0.25.1",
        "resampy==0.4.2"
    ]
    
    # Lista de paquetes de IA (opcionales)
    ai_packages = [
        "torch==2.1.2",
        "torchaudio==2.1.2",
        "demucs==4.0.1"
    ]
    
    print("📦 Instalando paquetes core...")
    core_success = True
    for package in core_packages:
        if not install_package(package):
            core_success = False
    
    print("\n🤖 Instalando paquetes de IA...")
    ai_success = True
    for package in ai_packages:
        if not install_package(package):
            print(f"⚠️  {package} falló, pero continuando...")
            ai_success = False
    
    print("\n" + "=" * 60)
    if core_success:
        print("✅ Instalación completada exitosamente!")
        if ai_success:
            print("🎯 Todos los procesadores de IA están disponibles")
            print("   - Demucs (alta calidad)")
            print("   - Advanced (calidad media)")
            print("   - Fast (procesamiento rápido)")
            print("   - Simple (fallback)")
        else:
            print("⚠️  Algunos procesadores de IA no están disponibles")
            print("   - Advanced (calidad media) ✅")
            print("   - Fast (procesamiento rápido) ✅")
            print("   - Simple (fallback) ✅")
            print("   - Demucs (alta calidad) ❌")
    else:
        print("❌ Error en la instalación de paquetes core")
        sys.exit(1)
    
    print("\n🚀 Tu aplicación de separación de audio está lista!")
    print("💡 El sistema seleccionará automáticamente el mejor procesador")

if __name__ == "__main__":
    main() 