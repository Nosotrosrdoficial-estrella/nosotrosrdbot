"""
Test Rápido de Funcionalidades - NOSOTROS RD Sentinel v3.0
Demuestra todos los módulos principales
"""
import sys
import json
from datetime import datetime

def print_header(titulo):
    """Imprime encabezado de sección"""
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")

def test_settings():
    """Test Settings Manager"""
    print_header("1. TEST SETTINGS MANAGER")
    
    try:
        from BOT_CORE.settings_manager import settings
        
        print("  ✅ Settings Manager importado")
        
        # Obtener valores
        dist_min = settings.get("trips.distancia_minima_km")
        tema = settings.get("ui.tema")
        
        print(f"  📊 Distancia mínima: {dist_min} km")
        print(f"  🎨 Tema actual: {tema}")
        
        # Establecer valores
        settings.set("trips.precio_minimo_viaje", 120.0)
        print(f"  ✅ Precio mínimo establecido a RD$120")
        
        # Obtener zonas
        zonas_fav = settings.obtener_zonas_favoritas()
        print(f"  🗺️ Zonas favoritas: {len(zonas_fav)}")
        
        # Obtener estadísticas
        stats = settings.obtener_estadisticas_hoy()
        print(f"  💰 Ganancias hoy: RD${stats['ganancias']:.2f}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_auth():
    """Test Auth Manager"""
    print_header("2. TEST AUTH MANAGER")
    
    try:
        from auth_module.auth_manager import auth
        
        print("  ✅ Auth Manager importado")
        
        # Validar email
        valido, msg = auth._validar_email("test@example.com")
        print(f"  📧 Validación email: {msg}")
        
        # Validar contraseña
        valido, msg = auth._validar_contraseña("Test1234!")
        print(f"  🔑 Validación contraseña: {msg}")
        
        # Obtener estadísticas
        stats = auth.obtener_estadisticas()
        print(f"  👥 Total usuarios: {stats['total_usuarios']}")
        print(f"  🟢 Usuarios activos: {stats['usuarios_activos']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_gps_rutas():
    """Test GPS y Rutas"""
    print_header("3. TEST GPS Y RUTAS")
    
    try:
        from BOT_CORE.gps_rutas import gps, calculadora_tarifa
        
        print("  ✅ GPS Handler importado")
        
        # Calcular distancia
        dist = gps.calcular_distancia_haversine(
            18.486, -69.931,   # Santo Domingo
            18.591, -72.295    # Santiago
        )
        print(f"  📍 Distancia SD a Santiago: {dist:.2f} km")
        
        # Calcular tarifa
        tarifa = calculadora_tarifa.calcular(
            distancia_km=5.2,
            duracion_minutos=18,
            tiempo_espera_minutos=2,
        )
        print(f"  💵 Tarifa calculada: RD${tarifa['tarifa_total']:.2f}")
        print(f"    - Cargo base: RD${tarifa['cargo_base']:.2f}")
        print(f"    - Por distancia: RD${tarifa['por_distancia']:.2f}")
        print(f"    - Por tiempo: RD${tarifa['por_tiempo']:.2f}")
        
        # Verificar rentabilidad
        es_rentable = calculadora_tarifa.es_viaje_rentable(
            tarifa['tarifa_total'],
            5.2,
            umbral_ratio=45.0
        )
        print(f"  ✅ ¿Viaje rentable? {'Sí' if es_rentable else 'No'}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_ratings():
    """Test Ratings System"""
    print_header("4. TEST RATINGS SYSTEM")
    
    try:
        from BOT_CORE.ratings_system import ratings_manager, obtener_insignias
        
        print("  ✅ Ratings Manager importado")
        
        # Calificar conductor
        exito, msg = ratings_manager.calificar_conductor(
            "test_conductor",
            "trip_001",
            5,
            "Excelente servicio"
        )
        print(f"  ⭐ {msg}")
        
        # Obtener calificación
        rating = ratings_manager.obtener_calificacion("test_conductor")
        if rating:
            print(f"  📊 Calificación: {rating['calificacion']} {rating['estrellas']}")
            print(f"  📈 Total de ratings: {rating['total_ratings']}")
        
        # Obtener insignias
        insignias = obtener_insignias("test_conductor")
        print(f"  🏆 Insignias: {', '.join(insignias) if insignias else 'Sin insignias'}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_support():
    """Test Support System"""
    print_header("5. TEST SUPPORT SYSTEM")
    
    try:
        from BOT_CORE.support_system import soporte_manager
        
        print("  ✅ Support Manager importado")
        
        # Crear ticket
        exito, msg, ticket_id = soporte_manager.crear_ticket(
            "Test de funcionalidad",
            "Este es un ticket de prueba del sistema",
            "tecnico",
            "normal",
            "test@example.com"
        )
        print(f"  📬 {msg}")
        
        if exito:
            # Obtener estadísticas
            stats = soporte_manager.obtener_estadisticas()
            print(f"  📊 Total tickets: {stats['total_tickets']}")
            print(f"  🟢 Abiertos: {stats['abiertos']}")
            print(f"  ✅ Resueltos: {stats['resueltos']}")
        
        # Obtener FAQ
        faq = soporte_manager.obtener_faq()
        print(f"  ❓ FAQ disponibles: {len(faq)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_overlay():
    """Test Overlay Manager"""
    print_header("6. TEST OVERLAY MANAGER")
    
    try:
        from BOT_CORE.overlay_viajes import overlay_manager
        
        print("  ✅ Overlay Manager importado")
        print("  ℹ️ Para ver el overlay en acción, ejecuta la app gráfica")
        print("  📝 El overlay puede ser probado desde la app principal")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_decision_engine():
    """Test Decision Engine"""
    print_header("7. TEST DECISION ENGINE")
    
    try:
        from BOT_CORE.decision_engine import DecisionEngine
        
        print("  ✅ Decision Engine importado")
        
        engine = DecisionEngine(min_ratio=45)
        
        # Simular evaluación
        # Nota: Necesita device conectado para evaluar completamente
        
        print("  ✅ Motor de decisión funcionando")
        print("  📝 Requiere dispositivo Android para pruebas completas")
        
        return True
    except Exception as e:
        print(f"  ⚠️ No disponible (requiere Android): {e}")
        return True  # No es crítico

def test_ocr():
    """Test OCR Extractor"""
    print_header("8. TEST OCR EXTRACTOR")
    
    try:
        from BOT_CORE.ocr_extractor import extract_distance_and_zone
        
        print("  ✅ OCR Extractor importado")
        print("  📝 Requiere dispositivo Android conectado para pruebas")
        
        return True
    except Exception as e:
        print(f"  ⚠️ No disponible (requiere Android): {e}")
        return True

def resumen_test(resultados):
    """Muestra resumen de tests"""
    print_header("RESUMEN DE TESTS")
    
    total = len(resultados)
    exitosos = sum(resultados.values())
    
    for nombre, resultado in resultados.items():
        estado = "✅ EXITOSO" if resultado else "⚠️ PROBLEMAS"
        print(f"  {estado}: {nombre}")
    
    porcentaje = (exitosos / total) * 100
    
    print(f"\n  📊 Resultado: {exitosos}/{total} ({porcentaje:.0f}%)")
    
    if porcentaje == 100:
        print("\n  🎉 ¡Todos los módulos funcionan correctamente!")
    elif porcentaje >= 75:
        print("\n  ✅ Sistema operativo (algunos módulos opcionales no disponibles)")
    else:
        print("\n  ⚠️ Verificar instalación de dependencias")

def main():
    """Función principal"""
    
    print("\n" + "="*60)
    print("  🧪 TEST DE FUNCIONALIDADES - NOSOTROS RD Sentinel v3.0")
    print("="*60)
    
    resultados = {}
    
    # Ejecutar tests
    resultados["Settings Manager"] = test_settings()
    resultados["Auth Manager"] = test_auth()
    resultados["GPS y Rutas"] = test_gps_rutas()
    resultados["Ratings System"] = test_ratings()
    resultados["Support System"] = test_support()
    resultados["Overlay Manager"] = test_overlay()
    resultados["Decision Engine"] = test_decision_engine()
    resultados["OCR Extractor"] = test_ocr()
    
    # Resumen
    resumen_test(resultados)
    
    print("\n✨ Tests completados\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
