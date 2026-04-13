from flask import Flask, request, render_template_string, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db()
    c = conn.cursor()
    filtro_activos = request.args.get('activos') == '1'
    if request.method == 'POST':
        hwid = request.form.get('hwid')
        nombre = request.form.get('nombre_socio')
        plan = request.form.get('plan')
        if hwid:
            fecha_vencimiento = calcular_vencimiento(plan)
            c.execute('INSERT OR IGNORE INTO dispositivos (hwid, nombre_socio, status, plan, fecha_vencimiento) VALUES (?, ?, ?, ?, ?)',
                      (hwid, nombre, 'pendiente', plan, fecha_vencimiento))
            conn.commit()
        # Cambiar status si se envía
        for key in request.form:
            if key.startswith('aprobar_'):
                c.execute('UPDATE dispositivos SET status=? WHERE hwid=?', ('aprobado', key.split('_',1)[1]))
                conn.commit()
            if key.startswith('bloquear_'):
                c.execute('UPDATE dispositivos SET status=? WHERE hwid=?', ('bloqueado', key.split('_',1)[1]))
                conn.commit()
    if filtro_activos:
        hoy = datetime.now().date()
        c.execute('SELECT * FROM dispositivos WHERE status="aprobado" AND fecha_vencimiento >= ?', (hoy.strftime('%Y-%m-%d'),))
    else:
        c.execute('SELECT * FROM dispositivos')
    dispositivos = c.fetchall()
    conn.close()
    html = CYBER_STYLE + '''
    <h2>ATM BOT - Centro de Socios</h2>
    <form method="post">
        <input name="hwid" placeholder="HWID" required>
        <input name="nombre_socio" placeholder="Nombre del socio">
        <select name="plan" required>
            <option value="1 Mes">1 Mes</option>
            <option value="3 Meses">3 Meses</option>
            <option value="1 Año">1 Año</option>
        </select>
        <button class="btn" type="submit">Registrar</button>
    </form>
    <form method="get" style="margin-top:10px;">
        <button class="btn" name="activos" value="1" type="submit">FILTRAR ACTIVOS</button>
        <a href="/" class="btn">Mostrar Todos</a>
    </form>
    <table>
        <tr>
            <th>HWID</th>
            <th>Nombre Socio</th>
            <th>Plan</th>
            <th>VENCIMIENTO</th>
            <th>Días Restantes</th>
            <th>Status</th>
            <th>Acciones</th>
        </tr>
        {% for d in dispositivos %}
        {% set status, color, dias_restantes = estado_visual(d['status'], d['fecha_vencimiento']) %}
        <tr>
            <td>{{ d['hwid'] }}</td>
            <td>{{ d['nombre_socio'] or '' }}</td>
            <td>{{ d['plan'] or '' }}</td>
            <td>{{ d['fecha_vencimiento'] or '' }}</td>
            <td>{{ dias_restantes }}</td>
            <td class="{{ color }}">{{ status }}</td>
            <td>
                <button class="btn" name="aprobar_{{ d['hwid'] }}" type="submit">APROBAR</button>
                <button class="btn" name="bloquear_{{ d['hwid'] }}" type="submit">BLOQUEAR</button>
            </td>
        </tr>
        {% endfor %}
    </table>
    <script>
    // JS para ocultar filas vencidas si se pulsa FILTRAR ACTIVOS
    document.addEventListener('DOMContentLoaded', function() {
        const urlParams = new URLSearchParams(window.location.search);
        if(urlParams.get('activos') === '1') {
            document.querySelectorAll('tr').forEach(function(row) {
                if(row.querySelector('.rojo')) row.style.display = 'none';
            });
        }
    });
    </script>
    '''
    return render_template_string(html, dispositivos=dispositivos, estado_visual=estado_visual)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
