[app]
title = ATM BOT
package.name = atmbot
package.domain = org.edwin.atmbot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# Punto de entrada
entrypoint = BOT_CORE/main.py

# Requerimientos
requirements = python3,kivy,requests,pillow,numpy,android

# Orientación
orientation = portrait

# Permisos de Android
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_PHONE_STATE

# SDK/NDK
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Ndk API
android.ndk_api = 21

# No forzar wakelock
android.wakelock = False

# Log level
log_level = 2

# Bootstrap Kivy
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
