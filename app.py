import os
import json
import bcrypt
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'nosotros_rd_sentinel_2026'
app.config['WTF_CSRF_ENABLED'] = True

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Base de datos simple (JSON)
DB_FILE = 'admin_db.json'
USERS_FILE = 'users_db.json'
NOTIFICATIONS_FILE = 'notifications_db.json'

# Configuración de email para notificaciones
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'tu_email@gmail.com'  # Cambiar por tu email
SMTP_PASS = 'tu_password'  # Cambiar por tu password o app password

# Modelo de Usuario Admin
class AdminUser(UserMixin):
    def __init__(self, id, email, password_hash, created_at):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

# Modelo de Usuario del Bot
class BotUser:
    def __init__(self, user_id, email, nombre, telefono, plan, estado, fecha_registro, tiempo_uso, ultimo_acceso):
        self.user_id = user_id
        self.email = email
        self.nombre = nombre
        self.telefono = telefono
        self.plan = plan
        self.estado = estado  # 'pendiente', 'aprobado', 'denegado', 'suspendido'
        self.fecha_registro = fecha_registro
        self.tiempo_uso = tiempo_uso  # en minutos
        self.ultimo_acceso = ultimo_acceso

# Funciones de base de datos
def load_db(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_db(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_admin_users():
    return load_db(DB_FILE)

def save_admin_users(users):
    save_db(DB_FILE, users)

def load_bot_users():
    return load_db(USERS_FILE)

def save_bot_users(users):
    save_db(USERS_FILE, users)

def load_notifications():
    return load_db(NOTIFICATIONS_FILE)

def save_notifications(notifs):
    save_db(NOTIFICATIONS_FILE, notifs)

@login_manager.user_loader
def load_user(user_id):
    users = load_admin_users()
    user_data = users.get(user_id)
    if user_data:
        return AdminUser(user_id, user_data['email'], user_data['password_hash'], user_data['created_at'])
    return None

# Formularios
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrar')

class NotificationForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    mensaje = TextAreaField('Mensaje', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('alerta', 'Alerta'), ('oferta', 'Oferta'), ('descuento', 'Descuento')])
    submit = SubmitField('Enviar Notificación')

# Funciones auxiliares
def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def get_user_stats():
    users = load_bot_users()
    total = len(users)
    aprobados = sum(1 for u in users.values() if u['estado'] == 'aprobado')
    pendientes = sum(1 for u in users.values() if u['estado'] == 'pendiente')
    denegados = sum(1 for u in users.values() if u['estado'] == 'denegado')
    tiempo_total = sum(u.get('tiempo_uso', 0) for u in users.values())
    return {
        'total': total,
        'aprobados': aprobados,
        'pendientes': pendientes,
        'denegados': denegados,
        'tiempo_total_minutos': tiempo_total,
        'tiempo_total_horas': round(tiempo_total / 60, 2)
    }

# Rutas públicas (para el bot)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ping')
def ping():
    return jsonify({"status": "online", "service": "NOSOTROS RD Sentinel"})

@app.route('/register_user', methods=['POST'])
def register_user():
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

    users = load_bot_users()
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
    save_bot_users(users)

    return jsonify({"success": True, "message": "Usuario registrado, pendiente de aprobación"})

@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()
    user_id = data.get('user_id')

    users = load_bot_users()
    user = users.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if user['estado'] != 'aprobado':
        return jsonify({"error": "Usuario no aprobado"}), 403

    # Actualizar último acceso y tiempo de uso
    user['ultimo_acceso'] = datetime.now().isoformat()
    user['tiempo_uso'] += 1  # Simular 1 minuto por login
    save_bot_users(users)

    return jsonify({"success": True, "user": user})

@app.route('/support_request', methods=['POST'])
def support_request():
    data = request.get_json()
    user_id = data.get('user_id')
    issue = data.get('issue')

    if not user_id or not issue:
        return jsonify({"error": "user_id e issue requeridos"}), 400

    # Aquí podrías guardar el ticket de soporte
    # Por ahora, solo loguear
    print(f"Soporte solicitado por {user_id}: {issue}")

    return jsonify({"success": True, "message": "Solicitud de soporte enviada"})

# Rutas de admin
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        users = load_admin_users()
        user_data = None
        for uid, udata in users.items():
            if udata['email'] == form.email.data:
                user_data = udata
                user_id = uid
                break

        if user_data and check_password_hash(user_data['password_hash'], form.password.data):
            user = AdminUser(user_id, user_data['email'], user_data['password_hash'], user_data['created_at'])
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Credenciales inválidas')

    return render_template('admin_login.html', form=form)

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Las contraseñas no coinciden')
            return render_template('admin_register.html', form=form)

        users = load_admin_users()
        # Verificar si ya existe
        for udata in users.values():
            if udata['email'] == form.email.data:
                flash('Email ya registrado')
                return render_template('admin_register.html', form=form)

        # Crear usuario
        user_id = str(len(users) + 1)
        users[user_id] = {
            'email': form.email.data,
            'password_hash': generate_password_hash(form.password.data),
            'created_at': datetime.now().isoformat()
        }
        save_admin_users(users)

        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html', form=form)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    users = load_bot_users()
    stats = get_user_stats()
    return render_template('admin_dashboard.html', users=users, stats=stats)

@app.route('/admin/users')
@login_required
def admin_users():
    users = load_bot_users()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/<user_id>/approve', methods=['POST'])
@login_required
def approve_user(user_id):
    users = load_bot_users()
    if user_id in users:
        users[user_id]['estado'] = 'aprobado'
        save_bot_users(users)
        # Enviar email de aprobación
        send_email(users[user_id]['email'], 'Cuenta Aprobada - NOSOTROS RD',
                  f'Hola {users[user_id]["nombre"]},\n\nTu cuenta ha sido aprobada. Ya puedes usar el servicio.')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<user_id>/deny', methods=['POST'])
@login_required
def deny_user(user_id):
    users = load_bot_users()
    if user_id in users:
        users[user_id]['estado'] = 'denegado'
        save_bot_users(users)
        # Enviar email de denegación
        send_email(users[user_id]['email'], 'Cuenta Denegada - NOSOTROS RD',
                  f'Hola {users[user_id]["nombre"]},\n\nTu solicitud de cuenta ha sido denegada.')
    return redirect(url_for('admin_users'))

@app.route('/admin/notifications', methods=['GET', 'POST'])
@login_required
def admin_notifications():
    form = NotificationForm()
    if form.validate_on_submit():
        users = load_bot_users()
        notifs = load_notifications()

        notif_id = str(len(notifs) + 1)
        notifs[notif_id] = {
            'titulo': form.titulo.data,
            'mensaje': form.mensaje.data,
            'tipo': form.tipo.data,
            'fecha': datetime.now().isoformat(),
            'enviados': []
        }

        # Enviar a todos los usuarios aprobados
        for user_id, user in users.items():
            if user['estado'] == 'aprobado':
                if send_email(user['email'], f'{form.titulo.data} - NOSOTROS RD', form.mensaje.data):
                    notifs[notif_id]['enviados'].append(user_id)

        save_notifications(notifs)
        flash(f'Notificación enviada a {len(notifs[notif_id]["enviados"])} usuarios')

    notifs = load_notifications()
    return render_template('admin_notifications.html', form=form, notifications=notifs)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)