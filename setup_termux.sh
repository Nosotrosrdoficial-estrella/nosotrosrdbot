#!/bin/bash
# ==============================================
#  ATM BOT - Script de instalación en Termux
# ==============================================

echo ">>> Actualizando paquetes..."
pkg update -y && pkg upgrade -y

echo ">>> Instalando dependencias base..."
pkg install -y python git clang libffi openssl

echo ">>> Instalando uv (gestor de paquetes rápido)..."
pip install uv

echo ">>> Instalando librerías del bot..."
pip install requests pillow numpy kivy

echo ">>> Clonando/actualizando el bot..."
if [ -d "ATM-bot" ]; then
    cd ATM-bot && git pull
else
    git clone https://github.com/francis09hd/atm-admin.git ATM-bot
    cd ATM-bot
fi

echo ">>> Lanzando ATM BOT..."
python BOT_CORE/main.py
