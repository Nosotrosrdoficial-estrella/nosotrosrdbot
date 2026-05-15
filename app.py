import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
# SECRET_KEY desde variable de entorno o valor por defecto seguro
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nosotros_rd_sentinel_2026_secure_key')

# Configuración de Flask-Login simplificada
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Rutas de archivos con soporte para Render Persistent Disks
DATA_DIR = '/data' if os.path.exists('/data') else os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(DATA_DIR, 'users_db.json')
ADMIN_FILE = os.path.join(DATA_DIR, 'admin_db.json')
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications_db.json')

# Configuración SMTP desde variables de entorno
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')

# Clave de acceso maestra Sentinel
ACCESS_KEY = "Diosamor"

class AdminUser(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

# FUNCIONES DE CARGA SEGURA (Evitan el Error 500)
def load_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"Error cargando {file_path}: {e}")
    return {}

def save_data(file_path, data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except (IOError, OSError) as e:
        print(f"Error guardando {file_path}: {e}")

@login_manager.user_loader
def load_user(user_id):
    admins = load_data(ADMIN_FILE)
    if user_id in admins:
        return AdminUser(user_id, admins[user_id]['email'], admins[user_id]['password_hash'])
    return None

# Función de envío de email con manejo de errores robusto
def send_email(to_email, subject, body):
    try:
        if not SMTP_USER or not SMTP_PASS:
            print("Advertencia: Credenciales SMTP no configuradas")
            return False

        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        print("Error: Credenciales SMTP inválidas")
        return False
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

# Función para validar clave de acceso Sentinel
def validate_access_key():
    key = request.headers.get('X-Access-Key') or request.args.get('key') or request.form.get('key')
    return key == ACCESS_KEY

# Función para obtener estadísticas de usuarios
def get_user_stats(users):
    total = len(users)
    aprobados = sum(1 for u in users.values() if u.get('estado') == 'aprobado')
    pendientes = sum(1 for u in users.values() if u.get('estado') == 'pendiente')
    denegados = sum(1 for u in users.values() if u.get('estado') == 'denegado')

    return {
        'total': total,
        'aprobados': aprobados,
        'pendientes': pendientes,
        'denegados': denegados
    }

# RUTA DE REGISTRO ULTRA-SIMPLIFICADA CON VALIDACIÓN
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if not validate_access_key():
        return jsonify({"error": "Acceso denegado - Clave Sentinel requerida"}), 403

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return "Datos requeridos faltantes", 400

        admins = load_data(ADMIN_FILE)
        user_id = str(len(admins) + 1)
        admins[user_id] = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        save_data(ADMIN_FILE, admins)
        return "Registro exitoso. <a href='/admin/login'>Ir al Login</a>"

    return '''
        <form method="post">
            <input type="email" name="email" placeholder="Tu Email" required><br>
            <input type="password" name="password" placeholder="Tu Clave" required><br>
            <button type="submit">Registrar Maestro</button>
        </form>
    '''

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        admins = load_data(ADMIN_FILE)

        for uid, udata in admins.items():
            if udata['email'] == email and check_password_hash(udata['password_hash'], password):
                user = AdminUser(uid, email, udata['password_hash'])
                login_user(user)
                return redirect(url_for('admin_dashboard'))
        return "Credenciales incorrectas"

    return '''
        <form method="post">
            <input type="email" name="email" placeholder="Email"><br>
            <input type="password" name="password" placeholder="Clave"><br>
            <button type="submit">Entrar al Sentinel</button>
        </form>
    '''

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    users = load_data(USERS_FILE)
    stats = get_user_stats(users)
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/admin/users')
@login_required
def admin_users():
    users = load_data(USERS_FILE)
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<user_id>/approve', methods=['POST'])
@login_required
def approve_user(user_id):
    users = load_data(USERS_FILE)
    if user_id in users:
        users[user_id]['estado'] = 'aprobado'
        save_data(USERS_FILE, users)

        # Enviar email de aprobación
        if send_email(users[user_id]['email'], "Cuenta Aprobada - Nosotros RD",
                     f"¡Felicidades! Tu cuenta ha sido aprobada. Ya puedes usar el bot."):
            flash("Usuario aprobado y email enviado")
        else:
            flash("Usuario aprobado pero error enviando email")
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<user_id>/deny', methods=['POST'])
@login_required
def deny_user(user_id):
    users = load_data(USERS_FILE)
    if user_id in users:
        users[user_id]['estado'] = 'denegado'
        save_data(USERS_FILE, users)

        # Enviar email de denegación
        if send_email(users[user_id]['email'], "Cuenta Denegada - Nosotros RD",
                     "Lo sentimos, tu solicitud ha sido denegada."):
            flash("Usuario denegado y email enviado")
        else:
            flash("Usuario denegado pero error enviando email")
    return redirect(url_for('admin_users'))

@app.route('/admin/notifications')
@login_required
def admin_notifications():
    notifications = load_data(NOTIFICATIONS_FILE)
    return render_template('admin_notifications.html', notifications=notifications)

@app.route('/admin/notifications/send', methods=['POST'])
@login_required
def send_notification():
    title = request.form.get('title')
    message = request.form.get('message')
    target_users = request.form.getlist('target_users')

    if not title or not message:
        flash("Título y mensaje requeridos")
        return redirect(url_for('admin_notifications'))

    users = load_data(USERS_FILE)
    notifications = load_data(NOTIFICATIONS_FILE)

    sent_count = 0
    for user_id in target_users:
        if user_id in users and users[user_id]['estado'] == 'aprobado':
            if send_email(users[user_id]['email'], title, message):
                sent_count += 1

    # Guardar notificación
    notif_id = str(len(notifications) + 1)
    notifications[notif_id] = {
        'title': title,
        'message': message,
        'target_users': target_users,
        'sent_count': sent_count,
        'timestamp': datetime.now().isoformat()
    }
    save_data(NOTIFICATIONS_FILE, notifications)

    flash(f"Notificación enviada a {sent_count} usuarios")
    return redirect(url_for('admin_notifications'))

@app.route('/admin/logout')
def logout():
    logout_user()
    return redirect(url_for('admin_login'))

# RUTAS PARA EL BOT CON VALIDACIÓN DE CLAVE
@app.route('/register_user', methods=['POST'])
def register_user():
    if not validate_access_key():
        return jsonify({"error": "Acceso denegado - Clave Sentinel requerida"}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos requeridos"}), 400

        user_id = data.get('user_id')
        email = data.get('email')
        nombre = data.get('nombre', '')
        telefono = data.get('telefono', '')
        plan = data.get('plan', '1 Mes')

        if not user_id or not email:
            return jsonify({"error": "user_id y email requeridos"}), 400

        users = load_data(USERS_FILE)
        if user_id in users:
            return jsonify({"error": "Usuario ya registrado"}), 409

        users[user_id] = {
            'user_id': user_id,
            'email': email,
            'nombre': nombre,
            'telefono': telefono,
            'plan': plan,
            'estado': 'pendiente',
            'fecha_registro': datetime.now().isoformat(),
            'tiempo_uso': 0,
            'ultimo_acceso': None
        }
        save_data(USERS_FILE, users)

        return jsonify({"success": True, "message": "Usuario registrado, pendiente de aprobación"})
    except Exception as e:
        print(f"Error en register_user: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/login_user', methods=['POST'])
def login_user():
    if not validate_access_key():
        return jsonify({"error": "Acceso denegado - Clave Sentinel requerida"}), 403

    try:
        data = request.get_json()
        user_id = data.get('user_id')

        users = load_data(USERS_FILE)
        user = users.get(user_id)

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if user['estado'] != 'aprobado':
            return jsonify({"error": "Usuario no aprobado"}), 403

        # Actualizar último acceso y tiempo de uso
        user['ultimo_acceso'] = datetime.now().isoformat()
        user['tiempo_uso'] += 1  # Simular 1 minuto por login
        save_data(USERS_FILE, users)

        return jsonify({"success": True, "user": user})
    except Exception as e:
        print(f"Error en login_user: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/support_request', methods=['POST'])
def support_request():
    if not validate_access_key():
        return jsonify({"error": "Acceso denegado - Clave Sentinel requerida"}), 403

    try:
        data = request.get_json()
        user_id = data.get('user_id')
        issue = data.get('issue')

        if not user_id or not issue:
            return jsonify({"error": "user_id e issue requeridos"}), 400

        # Aquí podrías guardar el ticket de soporte
        print(f"Soporte solicitado por {user_id}: {issue}")

        return jsonify({"success": True, "message": "Solicitud de soporte enviada"})
    except Exception as e:
        print(f"Error en support_request: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

# PING ULTRA-LIGERO CON ACTUALIZACIÓN OPCIONAL DE ACCESO
@app.route('/ping')
def ping():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            users = load_data(USERS_FILE)
            if user_id in users:
                users[user_id]['ultimo_acceso'] = datetime.now().isoformat()
                save_data(USERS_FILE, users)
        except Exception as e:
            print(f"Error actualizando acceso para {user_id}: {e}")

    return jsonify({"status": "online", "service": "NOSOTROS RD Sentinel"})

@app.route('/')
def home():
    return "<h1>Servidor Nosotros RD Online</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
