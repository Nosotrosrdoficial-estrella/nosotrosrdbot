# Gemini Protocol Bot

## Descripción
Bot modular avanzado para automatización y pruebas de seguridad en apps Android, con enfoque en sigilo, seguridad y adaptabilidad.

## Estructura de Carpetas
- `auth/`: Login seguro, fingerprint de hardware, kill-switch y cifrado AES-256
- `perception/`: Visión multimodal (UI-tree y OCR)
- `logic/`: Lógica de decisión y filtros
- `controller/`: Gestos humanos y sigilo
- `overlay/`: Interfaz flotante y kill-switch
- `traffic/`: Predicción de tráfico en tiempo real

## Instalación
1. Instala Python 3.10+
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura tu clave maestra y parámetros en `config.py`.
4. Conecta tu dispositivo Android con ADB y habilita depuración.

## Ejecución
```bash
python main.py
```

## Seguridad
- Clave maestra cifrada (AES-256)
- Fingerprint de hardware (HWID)
- Kill-switch flotante
- Logs y llaves cifrados

## Personalización
- Edita `config.py` para ajustar precios, distancias, zonas peligrosas y parámetros de tráfico.

## Stack Tecnológico
- Python 3.10+, PyQt6, uiautomator2, adbutils, easyocr, pycryptodome, requests

## Notas
- El overlay flotante requiere permisos especiales en Android.
- El bot es modular: si un módulo falla, los demás siguen funcionando.
- Para máxima seguridad, ejecuta en un entorno aislado y nunca compartas tu clave maestra.
