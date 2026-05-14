"""
Setup Inicial - NOSOTROS RD Sentinel v3.0
Configura todo el entorno para primer uso
"""
import os
import sys
import json
from datetime import datetime

def banner():
    """Muestra banner de bienvenida"""
    print("\n" + "="*60)
    print("🚀 NOSOTROS RD - Sentinel Bot v3.0 Setup Inicial")
    print("="*60 + "\n")

def crear_directorios():
    """Crea directorios necesarios"""
    print("📁 Creando directorios...")
    
    directorios = [
        "cache",
        "tickets",
        "logs",
        "backups",
        "configuracion",
    ]
    
    for dir_name in directorios:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"  ✅ {dir_name}/")

def instalar_dependencias():
    """Instala dependencias requeridas"""
    print("\n📦 Instalando dependencias...")
    print("  Esto puede tomar algunos minutos...\n")
    
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                          capture_output=True,
                          text=True)
    
    if result.returncode == 0:
        print("  ✅ Dependencias instaladas correctamente")
    else:
        print("  ⚠️ Posible problema con instalación:")
        print(result.stderr[:500])
        return False
    
    return True

def crear_config_inicial():
    """Crea archivo de configuración inicial"""
    print("\n⚙️ Creando configuración inicial...")
    
    # Usar settings_manager para crear el archivo
    try:
        from BOT_CORE.settings_manager import settings
        print("  ✅ Configuración guardada en sentinel_settings.json")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

def crear_usuario_demo():
    """Crea usuario demo para pruebas"""
    print("\n👤 Creando usuario de demostración...")
    
    try:
        from auth_module.auth_manager import auth
        
        exito, msg = auth.registrar(
            "demo@nosotrosrd.com",
            "Demo1234!",
            "+1-809-9999999",
            "Usuario Demo"
        )
        
        if exito:
            print(f"  ✅ {msg}")
            print("  📧 Email: demo@nosotrosrd.com")
            print("  🔑 Contraseña: Demo1234!")
        else:
            if "ya registrado" in msg.lower():
                print(f"  ℹ️ {msg}")
            else:
                print(f"  ⚠️ {msg}")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

def verificar_python():
    """Verifica versión de Python"""
    print("\n🐍 Verificando Python...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version_str} (OK)")
        return True
    else:
        print(f"  ❌ Python {version_str} (Se requiere 3.8+)")
        return False

def verificar_modulos():
    """Verifica módulos principales"""
    print("\n🔍 Verificando módulos disponibles...")
    
    modulos = {
        "flask": "Flask (servidor web)",
        "kivy": "Kivy (interfaz gráfica)",
        "requests": "Requests (HTTP)",
        "uiautomator2": "UIAutomator2 (Android)",
    }
    
    disponibles = 0
    
    for modulo, descripcion in modulos.items():
        try:
            __import__(modulo)
            print(f"  ✅ {descripcion}")
            disponibles += 1
        except ImportError:
            print(f"  ⚠️ {descripcion} (no instalado)")
    
    return disponibles >= 3  # Al menos 3 de 4

def mostrar_proximos_pasos():
    """Muestra próximos pasos"""
    print("\n" + "="*60)
    print("✅ SETUP COMPLETADO")
    print("="*60)
    
    print("\n📋 Próximos Pasos:")
    print("  1. Ejecutar la aplicación principal:")
    print("     python BOT_CORE/app_principal.py")
    print("\n  2. Credenciales de demo:")
    print("     Email: demo@nosotrosrd.com")
    print("     Contraseña: Demo1234!")
    print("\n  3. Documentación:")
    print("     Leer README_v3.md para más información")
    print("\n  4. Configurar parámetros:")
    print("     Desde el panel de Configuración en la app")
    
    print("\n📞 Soporte:")
    print("  Centro de Soporte disponible dentro de la aplicación")
    
    print("\n" + "="*60 + "\n")

def main():
    """Función principal del setup"""
    
    # Banner
    banner()
    
    # Verificaciones
    if not verificar_python():
        print("❌ Setup cancelado: versión de Python incompatible")
        sys.exit(1)
    
    # Crear directorios
    crear_directorios()
    
    # Instalar dependencias
    if not instalar_dependencias():
        print("⚠️ Continuar aún con posibles problemas...")
    
    # Verificar módulos
    print()
    verificar_modulos()
    
    # Crear configuración
    crear_config_inicial()
    
    # Crear usuario demo
    crear_usuario_demo()
    
    # Mostrar próximos pasos
    mostrar_proximos_pasos()
    
    print("✨ ¡Setup listo! Disfruta NOSOTROS RD - Sentinel Bot v3.0\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error durante setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
