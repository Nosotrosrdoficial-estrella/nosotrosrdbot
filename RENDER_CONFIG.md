# 🚀 Configuración de Sentinel Core en Render

## Problema diagnosticado:
**Error "Exited with status 1"** causado por:
- Flask-CORS no instalado en el entorno de Render
- Versión Python incorrecta especificada

## ✅ Cambios para arreglar:

### 1. **requirements.txt** 
Debe contener EXACTAMENTE:
```
flask
flask-cors
gunicorn
```

### 2. **runtime.txt**
Especifica la versión de Python:
```
python-3.11.9
```

### 3. **Procfile**
El comando de inicio:
```
web: gunicorn app:app
```

## 🔧 Instrucciones de Deploy en Render:

1. **GitHub está sincronizado**
   - Commit: `8d2a93a` incluye todos los archivos necesarios

2. **En Render Dashboard:**
   - Ir a tu servicio
   - **Settings** → **Build & Deploy**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (Render lo lee de Procfile)

3. **Variables de Entorno:**
   - NO setear `PORT` (Render lo asigna automáticamente)
   - El código lee `os.environ.get('PORT', 5000)`

4. **Redeploy:**
   - Click en "Deploy latest commit"
   - O simplemente hace push a GitHub (auto-redeploy)

## ✔️ Verificación Local:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Import test
python -c "from app import app; print('✓ OK')"

# Test con gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

## 🎯 Respuesta esperada en GET /

```json
{
  "status": "online",
  "message": "SENTINEL CORE v1.0 - STARK ACTIVE",
  "system_integrity": "100%"
}
```

## 📊 Status:

- ✅ app.py: Validado localmente
- ✅ requirements.txt: Todas las librerías instaladas (.venv311)
- ✅ Procfile: Correcto
- ✅ runtime.txt: Python 3.11.9 especificado
- ✅ GitHub: Sincronizado

**Si aún falla en Render:** Revisa los logs en Render Dashboard → Logs
