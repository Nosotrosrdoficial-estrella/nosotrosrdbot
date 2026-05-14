import os
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
# Usar variable de entorno para seguridad, o una por defecto fija
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nosotros_rd_sentinel_2026')
app.config['WTF_CSRF_ENABLED'] = True

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Rutas de persistencia para Render (/opt/render/project/src/...)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(ROOT_DIR, 'admin_db.json')
USERS_FILE = os.path.join(ROOT_DIR, 'users_db.json')
NOTIFICATIONS_FILE = os.path.join(ROOT_DIR, 'notifications_db.json')

# Configuración de email (Variables de entorno recomendadas)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = os.environ.get('SMTP_USER', 'tu_email@gmail.com')
SMTP_PASS = os.environ.get('SMTP_PASS', 'tu_app_password')

# --- MODELOS ---
class AdminUser(UserMixin):
    def __init__(self, id, email, password_hash, created_at):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

# --- PERSISTENCIA CORREGIDA ---
def load_db(file_path):
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except Exception as e:
        print(f"Aviso: DB vacía o error en {file_path}: {e}")
        return {}

def save_db(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error crítico guardando {file_path}: {e}")

@login_manager.user_loader
def load_user(user_id):
    users = load_db(DB_FILE)
    u = users.get(str(user_id))
    if u:
        return AdminUser(user_id, u['email'], u['password_hash'], u['created_at'])
    return None

# --- FORMULARIOS ---
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

# --- FUNCIONES AUXILIARES ---
def send_email(to_email, subject, body):
    # Si no hay credenciales, no rompe el servidor, solo avisa
    if SMTP_USER == 'tu_email@gmail.com' or not SMTP_PASS:
        print("DEBUG: Email no enviado (Faltan credenciales reales)")
        return False
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error SMTP: {e}")
        return False

# --- RUTAS PÚBLICAS / API BOT ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or not data.get('user_id'):
        return jsonify({"error": "user_id requerido"}), 400
    
    users = load_db(USERS_FILE)
    uid = str(data.get('user_id'))
    
    if uid in users:
        return jsonify({"error": "Ya registrado"}), 409

    users[uid] = {
        'user_id': uid,
        'email': data.get('email', ''),
        'nombre': data.get('nombre', 'Socio'),
        'telefono': data.get('telefono', ''),
        'plan': data.get('plan', 'Estándar'),
        'estado': 'pendiente',
        'fecha_registro': datetime.now().isoformat(),
        'tiempo_uso': 0
    }
    save_db(USERS_FILE, users)
    return jsonify({"success": True, "message": "Registro pendiente"})

# --- RUTAS ADMIN ---
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        users = load_db(DB_FILE)
        if any(u['email'] == form.email.data for u in users.values()):
            flash('Email ya existe')
            return render_template('admin_register.html', form=form)
        
        new_id = str(len(users) + 1)
        users[new_id] = {
            'email': form.email.data,
            'password_hash': generate_password_hash(form.password.data),
            'created_at': datetime.now().isoformat()
        }
        save_db(DB_FILE, users)
        flash('¡Registro exitoso! Inicia sesión.')
        return redirect(url_for('admin_login'))
    return render_template('admin_register.html', form=form)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        users = load_db(DB_FILE)
        for uid, udata in users.items():
            if udata['email'] == form.email.data and check_password_hash(udata['password_hash'], form.password.data):
                user = AdminUser(uid, udata['email'], udata['password_hash'], udata['created_at'])
                login_user(user)
                return redirect(url_for('admin_dashboard'))
        flash('Credenciales incorrectas')
    return render_template('admin_login.html', form=form)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    bot_users = load_db(USERS_FILE)
    return render_template('admin_dashboard.html', users=bot_users)

@app.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
