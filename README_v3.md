# NOSOTROS RD - Sentinel Bot v3.0
# Sistema de Automatización Avanzado para Viajes

## Características Principales

### 1. 🤖 Automatización Inteligente
- **Motor de Decisión**: Análisis automático de rentabilidad de viajes
- **OCR Multimodal**: Detección de precios, distancias y ubicaciones
- **Clicks Humanizados**: Curva Bezier con jitter para evadir detección
- **Validación de Zonas**: Geolocalización segura con restricciones personalizadas

### 2. ⚙️ Configuración Flexible
- **Panel de Control Web**: Interface Flask para gestión remota
- **Dashboard Kivy**: Aplicación desktop con UI moderna
- **Configuración Manual**: Control completo de parámetros
  - Zonas restringidas y favoritas
  - Distancias mínima y máxima
  - Precios y ratios de rentabilidad
  - Tema claro/oscuro
  - GPS y mapas inteligentes

### 3. 🗺️ GPS y Trazador de Rutas
- **Integración Google Maps & OpenStreetMap**
- **Cálculo de Distancias Haversine**
- **Estimación de Tráfico en Vivo**
- **Matriz de Distancias Multi-punto**

### 4. 💬 Sistema de Ratings y Reputación
- **Calificación de Conductores**: 1-5 estrellas con historial
- **Calificación de Pasajeros**: Filtrar por confiabilidad
- **Insignias y Logros**: Excelencia, veterano, sin reportes
- **Reportes y Suspensiones**: Control de usuarios problemáticos

### 5. 🎯 Overlay Flotante de Viajes
- **Burbuja Notificadora**: Aparece 10 segundos automáticamente
- **Info Completa**: Monto, distancia, duración, rating pasajero
- **Botones de Acción**: Aceptar/Rechazar con callbacks
- **Tema Dinámico**: Colores adaptativos oscuro/claro

### 6. 🔐 Autenticación y Seguridad
- **Sistema de Login Robusto**: Email + contraseña con encriptación PBKDF2
- **Registro de Usuarios**: Validación de datos + términos
- **Recuperación de Contraseña**: Tokens temporales expirables
- **Gestión de Sesiones**: Tokens con expiración de 7 días

### 7. 📞 Centro de Soporte Integrado
- **Sistema de Tickets**: Crear, seguir y resolver problemas
- **Categorización**: General, técnico, billing, seguridad, viaje
- **Bandeja de Mensajes**: Entrada y salida con contador
- **FAQ Dinámico**: Preguntas frecuentes integradas

### 8. 📊 Estadísticas y Monitoreo
- **Dashboard en Tiempo Real**: Ganancias, viajes, calificación
- **Historial de Viajes**: Detalles completos de cada operación
- **Análisis de Rentabilidad**: Ratios y tendencias
- **Exportación de Datos**: JSON persistente

---

## Instalación

### Requisitos
```bash
Python 3.8+
pip
virtualenv (opcional pero recomendado)
```

### Paso 1: Clonar/Descargar el Proyecto
```bash
cd "C:\Users\edwin\OneDrive\Desktop\ATM bot"
```

### Paso 2: Crear Ambiente Virtual (Recomendado)
```bash
python -m venv venv
.\venv\Scripts\Activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configuración Inicial
```bash
python setup_initial.py
```

---

## Uso

### Iniciar la Aplicación Principal
```bash
python BOT_CORE/app_principal.py
```

Esto abrirá:
1. Pantalla de Login
2. Registro o Recuperación
3. Dashboard Principal
4. Acceso a todas las funcionalidades

### Iniciar el Bot Automático (Servidor)
```bash
python flask_server.py
```

Accede a `http://localhost:5000` en tu navegador

### Iniciar Bot Android (Si tienes dispositivo conectado)
```bash
python RD_Bot/main.py
```

---

## Estructura de Archivos

```
BOT_CORE/
  ├── app_principal.py          ← APLICACIÓN PRINCIPAL (Ejecutar esto)
  ├── settings_manager.py        ← Gestión de configuración persistente
  ├── overlay_viajes.py          ← Overlay flotante de viajes
  ├── gps_rutas.py               ← GPS, mapas y trazador de rutas
  ├── ratings_system.py          ← Sistema de calificaciones
  ├── support_system.py          ← Centro de soporte
  ├── ui_auth_screens.py         ← Pantallas de login/registro
  ├── decision_engine.py         ← Motor de decisión de viajes
  ├── ocr_extractor.py           ← Extractor OCR
  └── sentinel_*.json            ← Archivos de configuración

auth_module/
  ├── auth_manager.py            ← Gestor de autenticación robusto
  ├── login.py                   ← Login legacy
  └── register.py                ← Registro legacy

RD_Bot/
  ├── main.py                    ← Bot para Android
  └── server_python/
      ├── vision.py              ← Detección de UI
      ├── stealth_engine.py      ← Clicks humanizados
      └── auth.py                ← Autenticación Android

SECURITY/
  ├── human_click.py             ← Clicks naturales
  └── stealth.py                 ← Técnicas de sigilosidad

flask_server.py                  ← Servidor web para panel remoto
app.py                           ← Panel web simple
main.py                          ← Aplicación Kivy inicial
```

---

## Configuración Personalizada

### Archivo: `sentinel_settings.json`

Se crea automáticamente con configuración por defecto. Puedes modificarlo manualmente:

```json
{
  "trips": {
    "distancia_minima_km": 0.5,
    "distancia_maxima_km": 15.0,
    "precio_minimo_viaje": 100.0,
    "rentabilidad_minima_ratio": 45.0
  },
  "zonas": {
    "favoritas": [
      {"nombre": "Centro", "lat": 18.486, "lon": -69.931, "radio_km": 2.0}
    ],
    "restringidas": [
      {"nombre": "Zona Roja", "lat": 18.500, "lon": -69.900, "radio_km": 1.5}
    ]
  },
  "ui": {
    "tema": "dark",
    "idioma": "es"
  },
  "notificaciones": {
    "overlay_duracion_segundos": 10,
    "overlay_posicion": "top-right"
  }
}
```

---

## API y Módulos Principales

### Settings Manager
```python
from BOT_CORE.settings_manager import settings

# Obtener valor
distancia_max = settings.get("trips.distancia_maxima_km")

# Establecer valor
settings.set("trips.precio_minimo_viaje", 150.0)

# Agregar zonas
settings.agregar_zona_favorita("Mi Lugar", lat, lon)
```

### Auth Manager
```python
from auth_module.auth_manager import auth

# Registrar usuario
exito, msg = auth.registrar("user@example.com", "Pass123!", "+1-809-2345678", "Juan")

# Login
exito, msg, token = auth.login("user@example.com", "Pass123!")

# Validar token
valido, sesion = auth.validar_token(token)
```

### Ratings Manager
```python
from BOT_CORE.ratings_system import ratings_manager

# Calificar conductor
ratings_manager.calificar_conductor("driver_001", "trip_123", 5, "Excelente")

# Obtener estadísticas
stats = ratings_manager.obtener_estadisticas("driver_001")
```

### Overlay Manager
```python
from BOT_CORE.overlay_viajes import overlay_manager

overlay_manager.mostrar_viaje(
    monto=350.0,
    distancia=5.2,
    duracion_estimada=18,
    calificacion_pasajero=4.9,
    ubicacion_salida="Centro",
    ubicacion_llegada="Aeropuerto",
)
```

### Soporte Manager
```python
from BOT_CORE.support_system import soporte_manager

# Crear ticket
exito, msg, ticket_id = soporte_manager.crear_ticket(
    "Problema con app",
    "No puedo aceptar viajes",
    "tecnico",
    "alta",
    "user@example.com"
)

# Obtener estadísticas
stats = soporte_manager.obtener_estadisticas()
```

---

## Funcionalidades Avanzadas

### 1. Validación de Zonas Seguras
```python
segura, msg = settings.verificar_zona_segura(lat, lon, hora="22:00")
```

### 2. Cálculo de Tarifa Inteligente
```python
from BOT_CORE.gps_rutas import calculadora_tarifa

tarifa = calculadora_tarifa.calcular(
    distancia_km=5.2,
    duracion_minutos=18,
    tiempo_espera_minutos=2,
    es_noche=False,
    hay_lluvia=False,
)
```

### 3. Trazador de Rutas
```python
from BOT_CORE.gps_rutas import mapas_osm

ruta = mapas_osm.obtener_ruta(
    lat_origen=18.486,
    lon_origen=-69.931,
    lat_destino=18.591,
    lon_destino=-72.295
)
```

### 4. Localización de Viajes Cercanos
```python
from BOT_CORE.gps_rutas import localizador

viajes_cercanos = localizador.obtener_viajes_en_radio(
    lat_actual=18.486,
    lon_actual=-69.931,
    lista_viajes=lista_viajes,
    distancia_maxima_km=30,
    tiempo_maximo_minutos=15,
)
```

---

## Comandos Útiles

```bash
# Ver versión de Python
python --version

# Listar paquetes instalados
pip list

# Actualizar paquete
pip install --upgrade nombre_paquete

# Resetear configuración
python -c "from BOT_CORE.settings_manager import resetear_configuracion; resetear_configuracion()"

# Ejecutar con output detallado
python BOT_CORE/app_principal.py -v
```

---

## Resolución de Problemas

### Error: "Kivy no disponible"
```bash
pip install kivy kivymd
```

### Error: "Módulo no encontrado"
Asegúrate de estar en el directorio correcto:
```bash
cd "C:\Users\edwin\OneDrive\Desktop\ATM bot"
```

### Error: "Puerto 5000 en uso"
Cambia el puerto en `flask_server.py`:
```python
app.run(port=5001)
```

### Resetear base de datos de usuarios
```bash
rm users_db.json  # o: del users_db.json (Windows)
```

---

## Seguridad

✅ **Implementado:**
- Encriptación PBKDF2 de contraseñas
- Tokens de sesión seguros
- Validación de entrada en todos los formularios
- Ofuscación de URLs
- Validación de HWID contra servidor

⚠️ **Recomendaciones:**
- Usar HTTPS en producción
- Cambiar `ACCESS_KEY` en config.py
- Usar firewall para restringir acceso
- Hacer backup regular de datos
- Usar VPN para conexiones remotas

---

## Deployment

### En Render.com
```bash
git push heroku main
```

### En máquina local
```bash
python flask_server.py
```

### En Android (con Buildozer)
```bash
buildozer android debug
adb install -r bin/app-debug.apk
```

---

## Contribuciones y Reportes

Para reportar bugs o sugerir funcionalidades:
1. Abre un ticket en "Centro de Soporte"
2. O contacta al equipo técnico

---

## Licencia

Uso exclusivo - NOSOTROS RD 2026

---

## Versión

**v3.0 - Última Generación**
- ✅ Configuración manual completa
- ✅ Login y registro robusto
- ✅ Overlay flotante
- ✅ GPS y rutas
- ✅ Ratings y reputación
- ✅ Centro de soporte integrado
- ✅ UI tema claro/oscuro
- ✅ Estadísticas en tiempo real

**Fecha**: 13 de Mayo de 2026
**Desarrollador**: Sentinel Team

---

## Contacto y Soporte

📧 Email: soporte@nosotrosrd.com
📞 WhatsApp: +1-809-SENTINEL
🌐 Web: https://nosotrosrd.com/soporte

---

*Gracias por usar NOSOTROS RD - Sentinel Bot v3.0*
