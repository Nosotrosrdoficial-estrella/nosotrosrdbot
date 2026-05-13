@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NOSOTROS RD - Sentinel</title>
        <style>
            body { background-color: #050505; color: #00ff41; font-family: 'Courier New', Courier, monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
            .panel { border: 2px solid #00ff41; padding: 40px; border-radius: 5px; box-shadow: 0 0 15px #00ff41; text-align: center; background: rgba(0, 20, 0, 0.9); }
            h1 { font-size: 2.5em; text-transform: uppercase; letter-spacing: 5px; margin-bottom: 10px; text-shadow: 2px 2px #000; }
            .status { font-size: 1.2em; border-top: 1px solid #00ff41; padding-top: 20px; margin-top: 20px; }
            .blink { animation: blinker 1.5s linear infinite; }
            @keyframes blinker { 50% { opacity: 0; } }
        </style>
    </head>
    <body>
        <div class="panel">
            <h1>NOSOTROS RD</h1>
            <p>SISTEMA DE CONTROL SENTINEL</p>
            <div class="status">
                ESTADO: <span class="blink">ONLINE</span><br>
                <small>ESPERANDO ENLACE DE DISPOSITIVO...</small>
            </div>
        </div>
    </body>
    </html>
    """