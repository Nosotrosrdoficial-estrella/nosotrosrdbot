import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Diosamor'

# Configuración de Flask-Login simplificada
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Archivos de base de datos
USERS_FILE = 'users_db.json'
ADMIN_FILE = 'admin_db.json'

class AdminUser(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

# FUNCIONES DE CARGA SEGURA (Evitan el Error 500)
def load_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_data(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error guardando: {e}")

@login_manager.user_loader
def load_user(user_id):
    admins = load_data(ADMIN_FILE)
    if user_id in admins:
        return AdminUser(user_id, admins[user_id]['email'], admins[user_id]['password_hash'])
    return None

# RUTA DE REGISTRO ULTRA-SIMPLIFICADA
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
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
    return f"<h1>Panel Nosotros RD</h1><p>Socios registrados: {len(users)}</p><a href='/admin/logout'>Salir</a>"

@app.route('/admin/logout')
def logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/')
def home():
    return "<h1>Servidor Nosotros RD Online</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
